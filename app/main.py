from fastapi import FastAPI
from .database import Base, engine
from .routers import issues, comments, reports
from app.routers import users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Issue Tracker API")

app.include_router(issues.router)
app.include_router(comments.router)
app.include_router(reports.router)
app.include_router(users.router)
