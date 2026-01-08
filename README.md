# Issue Tracker API

A backend service built using **FastAPI** and **PostgreSQL** that allows users to manage issues, comments, labels, bulk updates, CSV imports, and reports.  
The system demonstrates **real-world backend concepts** such as optimistic concurrency control, transactions, validation, and aggregation.

---

## Tech Stack

- **Backend Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Server:** Uvicorn

---

## 📁 Project Structure

issue-tracker-api/
│
├── app/
│ ├── main.py
│ ├── database.py
│ ├── models.py
│ ├── schemas.py
│ ├── deps.py
│ │
│ ├── routers/
│ │ ├── issues.py
│ │ ├── comments.py
│ │ ├── reports.py
│ │ └── users.py
│
├── requirements.txt
├── .env
└── README.md


---

---Create database on postgreSQL(pgAdmin etc)-----
CREATE DATABASE issue_tracker;

## ⚙️ Environment Setup

1️⃣ Create virtual environment
```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Configure environment variables
Create a .env file:

issue-tracker-api/
├── app/
├── requirements.txt
├── README.md
├── .gitignore
└── .env   ← create .env here

Add database url in .env like this:
DATABASE_URL=postgresql://postgres:password@localhost:5432/issue_tracker

4️⃣ Create database on postgreSQL
CREATE DATABASE issue_tracker;

▶️ Run the Server
python -m uvicorn app.main:app --reload

API will be available at:
http://127.0.0.1:8000

Swagger documentation:
http://127.0.0.1:8000/docs

🗄️ Database Design
Tables Implemented
users
issues
comments
labels
issue_labels
Key Features
Primary keys on all tables
Foreign key constraints for relationships
Unique constraint on label names
Indexes on frequently queried columns
version column on issues for optimistic locking


🔑 Core Features
1️⃣ Issue Management (CRUD + Concurrency)
Create, read, update, and list issues
Optimistic concurrency control using a version column
Conflicting updates return 409 Conflict
2️⃣ Comments
Add comments to issues
Non-empty body validation
Author validation via foreign keys
3️⃣ Labels
Unique labels
Many-to-many relationship with issues
Atomic label replacement
4️⃣ Bulk Status Update
Transactional bulk update of issue statuses
Rolls back if any issue violates rules
5️⃣ CSV Import
Upload CSV file for issue creation
Row-by-row validation
Partial success supported
Returns detailed summary report
6️⃣ Reports
Top Assignees: Aggregated count of issues per assignee
Average Resolution Time: Average time between issue creation and resolution
⭐ Bonus
Issue timeline endpoint showing full issue history


📌 API Endpoints
Users
POST /users – Create user
GET /users – List users
Issues
POST /issues – Create issue
GET /issues – List issues (filter supported)
GET /issues/{id} – Get issue details
PATCH /issues/{id} – Update issue (version check)
PUT /issues/{id}/labels – Replace labels
POST /issues/bulk-status – Bulk status update
POST /issues/import – CSV import
GET /issues/{id}/timeline – Issue timeline (bonus)
Comments
POST /issues/{id}/comments – Add comment
Reports
GET /reports/top-assignees
GET /reports/latency


📘 Issue Tracker API – Endpoints with Examples
Base URL
http://127.0.0.1:8000

👤 USERS API
1️⃣ Create User
POST /users
Input (JSON)
{
  "name": "Alice"
}
Output
{
  "id": 1,
  "name": "Alice"
}
2️⃣ List Users
GET /users
Output
[
  {
    "id": 1,
    "name": "Alice"
  },
  {
    "id": 2,
    "name": "Bob"
  }
]
🐞 ISSUES API
3️⃣ Create Issue
POST /issues
Input
{
  "title": "Login page bug",
  "assignee_id": 1
}
Output
{
  "id": 1,
  "title": "Login page bug",
  "status": "open",
  "version": 1,
  "assignee_id": 1
}
4️⃣ List Issues (Filtering)
GET /issues?status=open
Output
[
  {
    "id": 1,
    "title": "Login page bug",
    "status": "open",
    "version": 1
  }
]
5️⃣ Get Issue by ID
GET /issues/1
Output
{
  "id": 1,
  "title": "Login page bug",
  "status": "open",
  "version": 1,
  "assignee_id": 1,
  "comments": [],
  "labels": []
}
6️⃣ Update Issue (Optimistic Locking)
PATCH /issues/1
Input
{
  "status": "closed",
  "version": 1
}
Output
{
  "id": 1,
  "title": "Login page bug",
  "status": "closed",
  "version": 2,
  "resolved_at": "2026-01-08T10:15:30"
}
❌ Wrong version
{
  "status": "open",
  "version": 1
}
Output
409 Conflict
{
  "detail": "Version conflict"
}
💬 COMMENTS API
7️⃣ Add Comment
POST /issues/1/comments
Input
{
  "body": "Bug reproduced and assigned",
  "author_id": 2
}
Output
{
  "id": 1,
  "body": "Bug reproduced and assigned",
  "issue_id": 1,
  "author_id": 2
}
❌ Empty body:
400 Bad Request
🏷️ LABELS API
8️⃣ Replace Labels (Atomic)
PUT /issues/1/labels
Input
{
  "labels": ["bug", "urgent"]
}
Output
{
  "issue_id": 1,
  "labels": ["bug", "urgent"]
}
🔁 BULK UPDATE API
9️⃣ Bulk Status Update (Transactional)
POST /issues/bulk-status
Input
{
  "issue_ids": [1, 2],
  "status": "closed"
}
Output
{
  "updated_issues": [1, 2],
  "new_status": "closed"
}
❌ If one issue is invalid:
{
  "issue_ids": [1, 999],
  "status": "closed"
}
Output
400 Bad Request
{
  "detail": "One or more issues not found"
}
(All updates rolled back)
📄 CSV IMPORT API
🔟 Import Issues via CSV
POST /issues/import
Body → form-data
Key	Type	Value
file	File	issues.csv
Sample CSV
title,assignee_id,status
Login bug,1,open
Payment issue,2,closed
,1,open
Invalid user,999,open
Output
{
  "total_rows": 4,
  "created": 2,
  "failed": 2,
  "errors": [
    {
      "row": 3,
      "error": "Title is required"
    },
    {
      "row": 4,
      "error": "Invalid assignee_id"
    }
  ]
}
📊 REPORTS API
1️⃣1️⃣ Top Assignees
GET /reports/top-assignees
Output
[
  {
    "assignee_id": 1,
    "total": 3
  },
  {
    "assignee_id": 2,
    "total": 1
  }
]
1️⃣2️⃣ Average Resolution Time
GET /reports/latency
Output (if resolved issues exist)
{
  "average_resolution_time": "0:02:45.123456"
}
If no resolved issues:
{
  "average_resolution_time": null
}
🕒 BONUS: TIMELINE API
1️⃣3️⃣ Issue Timeline
GET /issues/1/timeline
Output
{
  "issue_id": 1,
  "timeline": [
    {
      "event": "issue_created",
      "timestamp": "2026-01-08T09:10:00",
      "details": {
        "title": "Login bug",
        "assignee_id": 1
      }
    },
    {
      "event": "comment_added",
      "timestamp": "2026-01-08T09:15:12",
      "details": {
        "author_id": 2,
        "body": "Bug reproduced"
      }
    },
    {
      "event": "issue_closed",
      "timestamp": "2026-01-08T09:25:30",
      "details": {
        "status": "closed"
      }
    }
  ]
}
Swagger UI
You can also test everything interactively at:
http://127.0.0.1:8000/docs# issue-tracker-api


🗄️ Database Schema
The application uses PostgreSQL with the following schema.
All tables are created and managed using SQLAlchemy ORM, with constraints enforced at the database level.
🔹 users
Stores system users who can be assignees or comment authors.
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);
Constraints
id → Primary Key
🔹 issues
Stores issues reported in the system.
CREATE TABLE issues (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    assignee_id INTEGER REFERENCES users(id),
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);
Constraints & Indexes
assignee_id → Foreign Key → users(id)
version → Used for optimistic concurrency control
Indexes:
CREATE INDEX idx_issues_status ON issues(status);
CREATE INDEX idx_issues_assignee ON issues(assignee_id);
🔹 comments
Stores comments added to issues.
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    issue_id INTEGER REFERENCES issues(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Constraints & Indexes
issue_id → Foreign Key → issues(id)
author_id → Foreign Key → users(id)
Index:
CREATE INDEX idx_comments_issue ON comments(issue_id);
🔹 labels
Stores unique labels that can be assigned to issues.
CREATE TABLE labels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);
Constraints
name → Unique
🔹 issue_labels
Join table for many-to-many relationship between issues and labels.
CREATE TABLE issue_labels (
    issue_id INTEGER REFERENCES issues(id) ON DELETE CASCADE,
    label_id INTEGER REFERENCES labels(id) ON DELETE CASCADE,
    PRIMARY KEY (issue_id, label_id)
);
Constraints
Composite Primary Key (issue_id, label_id)
Prevents duplicate label assignments
