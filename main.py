from datetime import date, datetime
from enum import Enum
from random import randint
from typing import Any, Optional
from fastapi import Depends, FastAPI, HTTPException, status
from db.database import get_db
from sqlalchemy.orm import Session
from models.task_model import CreateTask, Task, UpdateTask
from db.model.db_model import TaskTable, extract_enum_value

app = FastAPI(root_path="/api/v1")

@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    return {"message": "Great job, the server is running!"}

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: CreateTask, db_session: Session = Depends(get_db)) -> Task:
    # Use exists() for more efficient duplicate check
    title_exists = db_session.query(
        db_session.query(TaskTable).filter(TaskTable.title == task.title).exists()
    ).scalar()
    
    if title_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task with this title already exists")
    
    # Convert Pydantic model to SQLAlchemy model (extract enum values for SQLite)
    db_task = TaskTable.from_pydantic(task)
    
    # Save to database
    db_session.add(db_task)
    db_session.commit()
    db_session.refresh(db_task)
    
    # Convert back to Pydantic model for response
    task_response = Task(**db_task.to_dict())
    return task_response

@app.get("/tasks", status_code=status.HTTP_200_OK)
async def get_all_tasks(
    db_session: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    assignee_filter: Optional[str] = None
) -> dict[str, list[Task] | int]:
    # Build query with filters
    query = db_session.query(TaskTable)
    
    # Apply filters if provided
    if status_filter:
        query = query.filter(TaskTable.status == status_filter)
    if priority_filter:
        query = query.filter(TaskTable.priority == priority_filter)
    if assignee_filter:
        query = query.filter(TaskTable.assignee == assignee_filter)
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply pagination with limit to prevent loading too many records
    db_tasks = query.offset(skip).limit(min(limit, 100)).all()

    # Convert SQLAlchemy models to Pydantic models for response
    tasks_response = [Task(**db_task.to_dict()) for db_task in db_tasks]
    return {
        "tasks": tasks_response,
        "total": total_count,
        "skip": skip,
        "limit": min(limit, 100)
    }

@app.get("/tasks/{id}", status_code=status.HTTP_200_OK)
async def get_task(id: int, db_session: Session = Depends(get_db)) -> Task:
    # Query the database using SQLAlchemy model
    db_task = db_session.query(TaskTable).filter(TaskTable.id == id).first()
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Convert SQLAlchemy model to Pydantic model for response
    task_response = Task(**db_task.to_dict())
    return task_response

@app.put("/tasks/{id}", status_code=status.HTTP_200_OK)
async def update_task(id: int, update_task: UpdateTask, db_session: Session = Depends(get_db)) -> Task:
    task = db_session.query(TaskTable).filter(TaskTable.id == id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Update task in place for better performance
    if update_task.title is not None:
        task.title = update_task.title
    if update_task.description is not None:
        task.description = update_task.description
    if update_task.status is not None:
        task.status = extract_enum_value(update_task.status)
    if update_task.priority is not None:
        task.priority = extract_enum_value(update_task.priority)
    if update_task.assignee is not None:
        task.assignee = update_task.assignee if isinstance(update_task.assignee, str) else update_task.assignee.value
    if update_task.due_date is not None:
        task.due_date = update_task.due_date
    
    task.updated_at = datetime.now()
    task.updated_by = update_task.updated_by
    
    db_session.commit()
    db_session.refresh(task)
    return Task(**task.to_dict())

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int, db_session: Session = Depends(get_db)):
    task = db_session.query(TaskTable).filter(TaskTable.id == id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db_session.delete(task)
    db_session.commit()
    return {"message": "Task deleted successfully"}