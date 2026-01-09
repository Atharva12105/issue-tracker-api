from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.deps import get_db
from app.models import Issue

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/top-assignees")
def top_assignees(db: Session = Depends(get_db)):
    results = (
        db.query(
            Issue.assignee_id,
            func.count(Issue.id).label("total")
        )
        .group_by(Issue.assignee_id)
        .all()
    )

    return [
        {
            "assignee_id": assignee_id,
            "total": total
        }
        for assignee_id, total in results
    ]



@router.get("/latency")
def avg_latency(db: Session = Depends(get_db)):
    avg = db.query(
        func.avg(Issue.resolved_at - Issue.created_at)
    ).scalar()

    return {
        "average_resolution_time": str(avg) if avg else None
    }

