from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("")
def create_user(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if not data.name.strip():
        raise HTTPException(status_code=400, detail="User name cannot be empty")

    user = models.User(name=data.name.strip())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("")
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()
