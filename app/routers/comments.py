from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/issues/{issue_id}/comments", tags=["Comments"])

@router.post("")
def add_comment(issue_id: int, data: schemas.CommentCreate, db: Session = Depends(get_db)):
    if not data.body.strip():
        raise HTTPException(400, "Empty comment")

    comment = models.Comment(issue_id=issue_id, **data.dict())
    db.add(comment)
    db.commit()
    return comment
