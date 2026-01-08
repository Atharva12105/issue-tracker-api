from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..deps import get_db
from sqlalchemy.exc import IntegrityError
from fastapi import UploadFile, File
import csv
import io
from datetime import datetime

router = APIRouter(prefix="/issues", tags=["Issues"])

@router.post("")
def create_issue(data: schemas.IssueCreate, db: Session = Depends(get_db)):
    issue = models.Issue(**data.dict())
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue

@router.get("")
def list_issues(db: Session = Depends(get_db), status: str = None):
    q = db.query(models.Issue)
    if status:
        q = q.filter(models.Issue.status == status)
    return q.all()

@router.get("/{issue_id}")
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    return {
        "id": issue.id,
        "title": issue.title,
        "status": issue.status,
        "version": issue.version,
        "assignee_id": issue.assignee_id,
        "created_at": issue.created_at,
        "resolved_at": issue.resolved_at,
        "comments": [
            {
                "id": c.id,
                "body": c.body,
                "author_id": c.author_id
            } for c in issue.comments
        ],
        "labels": [label.name for label in issue.labels]
    }
 
@router.get("/{issue_id}/timeline")
def issue_timeline(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    timeline = []

    # Issue created
    timeline.append({
        "event": "issue_created",
        "timestamp": issue.created_at,
        "details": {
            "title": issue.title,
            "assignee_id": issue.assignee_id
        }
    })

    # Status resolved
    if issue.resolved_at:
        timeline.append({
            "event": "issue_closed",
            "timestamp": issue.resolved_at,
            "details": {
                "status": issue.status
            }
        })

    # Comments
    for comment in issue.comments:
        timeline.append({
            "event": "comment_added",
            "timestamp": comment.created_at,
            "details": {
                "comment_id": comment.id,
                "author_id": comment.author_id,
                "body": comment.body
            }
        })

    # Labels snapshot
    if issue.labels:
        timeline.append({
            "event": "labels_updated",
            "timestamp": issue.created_at,
            "details": {
                "labels": [label.name for label in issue.labels]
            }
        })

    # Sort timeline chronologically
    timeline.sort(key=lambda x: x["timestamp"])

    return {
        "issue_id": issue.id,
        "timeline": timeline
    }
   
@router.put("/{issue_id}/labels")
def replace_labels(
    issue_id: int,
    data: schemas.LabelReplace,
    db: Session = Depends(get_db)
):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    try:
        # Remove existing labels
        issue.labels.clear()

        # Add / reuse labels
        for label_name in data.labels:
            label = (
                db.query(models.Label)
                .filter(models.Label.name == label_name)
                .first()
            )
            if not label:
                label = models.Label(name=label_name)
                db.add(label)
                db.flush()  # ensures label.id exists

            issue.labels.append(label)

        db.commit()
        db.refresh(issue)

        return {
            "issue_id": issue.id,
            "labels": [l.name for l in issue.labels]
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk-status")
def bulk_status_update(
    data: schemas.BulkStatusUpdate,
    db: Session = Depends(get_db)
):
    try:
        issues = (
            db.query(models.Issue)
            .filter(models.Issue.id.in_(data.issue_ids))
            .all()
        )

        if len(issues) != len(data.issue_ids):
            raise HTTPException(
                status_code=400,
                detail="One or more issues not found"
            )

        # Business rule example:
        # Do not close already closed issues
        for issue in issues:
            if issue.status == "closed" and data.status == "closed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Issue {issue.id} already closed"
                )

        # Update all issues
        for issue in issues:
            issue.status = data.status
            issue.version += 1

        db.commit()

        return {
            "updated_issues": [issue.id for issue in issues],
            "new_status": data.status
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# @router.patch("/{issue_id}")
# def update_issue(issue_id: int, data: schemas.IssueUpdate, db: Session = Depends(get_db)):
#     issue = db.query(models.Issue).get(issue_id)
#     if issue.version != data.version:
#         raise HTTPException(status_code=409, detail="Version conflict")

#     for k, v in data.dict(exclude={"version"}).items():
#         if v is not None:
#             setattr(issue, k, v)

#     issue.version += 1
#     db.commit()
#     return issue

@router.patch("/{issue_id}")
def update_issue(
    issue_id: int,
    data: schemas.IssueUpdate,
    db: Session = Depends(get_db)
):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Optimistic locking check
    if issue.version != data.version:
        raise HTTPException(status_code=409, detail="Version conflict")

    # Update allowed fields
    for key, value in data.dict(exclude={"version"}).items():
        if value is not None:
            setattr(issue, key, value)

    # Set resolved_at ONLY when status becomes closed
    if data.status == "closed":
        issue.resolved_at = datetime.utcnow()

    # Increment version after successful update
    issue.version += 1

    db.commit()
    db.refresh(issue)

    return issue

@router.post("/import")
def import_issues_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    total_rows = 0
    created = 0
    failed = 0
    errors = []

    for idx, row in enumerate(reader, start=1):
        total_rows += 1
        try:
            title = row.get("title")
            assignee_id = row.get("assignee_id")
            status = row.get("status", "open")

            if not title or not title.strip():
                raise ValueError("Title is required")

            if assignee_id:
                assignee_id = int(assignee_id)
                user = db.query(models.User).filter(models.User.id == assignee_id).first()
                if not user:
                    raise ValueError("Invalid assignee_id")
            else:
                assignee_id = None

            issue = models.Issue(
                title=title.strip(),
                assignee_id=assignee_id,
                status=status
            )

            db.add(issue)
            db.commit()
            created += 1

        except Exception as e:
            db.rollback()
            failed += 1
            errors.append({
                "row": idx,
                "error": str(e)
            })

    return {
        "total_rows": total_rows,
        "created": created,
        "failed": failed,
        "errors": errors
    }

