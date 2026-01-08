from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

issue_labels = Table(
    "issue_labels",
    Base.metadata,
    Column("issue_id", ForeignKey("issues.id")),
    Column("label_id", ForeignKey("labels.id"))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    status = Column(String, default="open")
    assignee_id = Column(Integer, ForeignKey("users.id"))
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

    comments = relationship("Comment", back_populates="issue")
    labels = relationship("Label", secondary=issue_labels)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    body = Column(String, nullable=False)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    issue = relationship("Issue", back_populates="comments")

class Label(Base):
    __tablename__ = "labels"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
