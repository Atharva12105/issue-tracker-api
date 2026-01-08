from pydantic import BaseModel
from typing import List, Optional

class IssueCreate(BaseModel):
    title: str
    assignee_id: Optional[int]

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    version: int

class CommentCreate(BaseModel):
    body: str
    author_id: int

class LabelReplace(BaseModel):
    labels: List[str]
    
class BulkStatusUpdate(BaseModel):
    issue_ids: List[int]
    status: str
    
class CSVImportSummary(BaseModel):
    total_rows: int
    created: int
    failed: int
    errors: list

class UserCreate(BaseModel):
    name: str
