from datetime import date, datetime
from enum import Enum
from random import randint
from typing import Any
from fastapi import Depends, FastAPI, HTTPException, status
from db.database import get_db
from sqlalchemy.orm import Session
from models.task_model import CreateTask, Task, UpdateTask
from db.model.db_model import TaskTable

# Get a database session
get_db()

app = FastAPI(root_path="/api/v1")

@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    return {"message": "Great job, the server is running!"}

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: CreateTask, db_session: Session = Depends(get_db)) -> Task:
    # Check if task with same title exists
    if db_session.query(TaskTable).filter(TaskTable.title == task.title).first():
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
async def get_all_tasks( db_session: Session = Depends(get_db)) -> dict[str, list[Task]]:
    # Query the database using SQLAlchemy model
    db_tasks = db_session.query(TaskTable).all()

    # Convert SQLAlchemy models to Pydantic models for response
    tasks_response = [Task(**db_task.to_dict()) for db_task in db_tasks]
    return {"tasks": tasks_response}

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
    
    updated_task = update_task.to_db_model(existing_task=task)
    db_session.merge(updated_task)
    db_session.commit()
    return Task(**updated_task.to_dict())

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int, db_session: Session = Depends(get_db)):
    task = db_session.query(TaskTable).filter(TaskTable.id == id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db_session.delete(task)
    db_session.commit()
    return {"message": "Task deleted successfully"}