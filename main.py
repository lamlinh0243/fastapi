from contextlib import asynccontextmanager
from typing import Generator

import sqlite3

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, model_validator


DATABASE_URL = "todo.db"


# =========================
# Database
# =========================

def get_db() -> Generator[sqlite3.Connection, None, None]:
    db = sqlite3.connect(DATABASE_URL)
    db.row_factory = sqlite3.Row

    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    db = sqlite3.connect(DATABASE_URL)

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed INTEGER NOT NULL DEFAULT 0,
            priority INTEGER NOT NULL DEFAULT 1
        )
        """
    )

    db.commit()
    db.close()


# =========================
# Lifespan
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")
    create_tables()

    yield

    print("Shutting down application...")


# =========================
# FastAPI application
# =========================

app = FastAPI(
    title="Todo API",
    description="FastAPI homework project",
    version="1.0.0",
    lifespan=lifespan,
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Pydantic models
# =========================

class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = None
    completed: bool = False
    priority: int = Field(default=1, ge=1, le=5)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=100)
    description: str | None = None
    completed: bool | None = None
    priority: int | None = Field(default=None, ge=1, le=5)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value

    @model_validator(mode="after")
    def validate_update(self):
        if (
            self.title is None
            and self.description is None
            and self.completed is None
            and self.priority is None
        ):
            raise ValueError("At least one field must be provided")

        return self


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    priority: int


# =========================
# Health endpoints
# =========================

@app.get("/health/live")
def health_live():
    return {
        "status": "alive"
    }


@app.get("/health/ready")
def health_ready(db: sqlite3.Connection = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {
            "status": "ready"
        }
    except sqlite3.Error:
        raise HTTPException(
            status_code=503,
            detail="Database is not ready"
        )


# =========================
# CREATE
# =========================

@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(
    todo: TodoCreate,
    db: sqlite3.Connection = Depends(get_db),
):
    cursor = db.execute(
        """
        INSERT INTO todos
        (title, description, completed, priority)
        VALUES (?, ?, ?, ?)
        """,
        (
            todo.title,
            todo.description,
            int(todo.completed),
            todo.priority,
        ),
    )

    db.commit()

    todo_id = cursor.lastrowid

    row = db.execute(
        "SELECT * FROM todos WHERE id = ?",
        (todo_id,),
    ).fetchone()

    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"]),
        "priority": row["priority"],
    }


# =========================
# GET LIST
# =========================

@app.get("/todos", response_model=list[TodoResponse])
def get_todos(
    db: sqlite3.Connection = Depends(get_db),
):
    rows = db.execute(
        "SELECT * FROM todos ORDER BY id"
    ).fetchall()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "completed": bool(row["completed"]),
            "priority": row["priority"],
        }
        for row in rows
    ]


# =========================
# GET DETAIL
# =========================

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(
    todo_id: int,
    db: sqlite3.Connection = Depends(get_db),
):
    row = db.execute(
        "SELECT * FROM todos WHERE id = ?",
        (todo_id,),
    ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"]),
        "priority": row["priority"],
    }


# =========================
# UPDATE
# =========================

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo: TodoUpdate,
    db: sqlite3.Connection = Depends(get_db),
):
    existing = db.execute(
        "SELECT * FROM todos WHERE id = ?",
        (todo_id,),
    ).fetchone()

    if existing is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    title = (
        todo.title
        if todo.title is not None
        else existing["title"]
    )

    description = (
        todo.description
        if todo.description is not None
        else existing["description"]
    )

    completed = (
        todo.completed
        if todo.completed is not None
        else bool(existing["completed"])
    )

    priority = (
        todo.priority
        if todo.priority is not None
        else existing["priority"]
    )

    db.execute(
        """
        UPDATE todos
        SET title = ?,
            description = ?,
            completed = ?,
            priority = ?
        WHERE id = ?
        """,
        (
            title,
            description,
            int(completed),
            priority,
            todo_id,
        ),
    )

    db.commit()

    row = db.execute(
        "SELECT * FROM todos WHERE id = ?",
        (todo_id,),
    ).fetchone()

    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"]),
        "priority": row["priority"],
    }


# =========================
# DELETE
# =========================

@app.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int,
    db: sqlite3.Connection = Depends(get_db),
):
    existing = db.execute(
        "SELECT * FROM todos WHERE id = ?",
        (todo_id,),
    ).fetchone()

    if existing is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    db.execute(
        "DELETE FROM todos WHERE id = ?",
        (todo_id,),
    )

    db.commit()

    return {
        "message": "Todo deleted successfully"
    }