from sqlalchemy import Column, Integer, String, DateTime, Date
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

Base = declarative_base()

def extract_enum_value(value):
    """Helper function to extract value from Enum or return as-is"""
    return value.value if isinstance(value, Enum) else value

class TaskTable(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    status = Column(String, nullable=False, index=True)  # Index for filtering by status
    priority = Column(String, nullable=False, index=True)  # Index for filtering by priority
    assignee = Column(String(100), nullable=False, index=True)  # Index for filtering by assignee
    created_at = Column(DateTime, nullable=False, index=True)  # Index for sorting by date
    updated_at = Column(DateTime, nullable=False)
    created_by = Column(String, nullable=False)
    updated_by = Column(String, nullable=False)
    due_date = Column(Date, nullable=True, index=True)  # Index for filtering by due date

    @classmethod
    def from_pydantic(cls, task):
        """Create a TaskTable instance from a Pydantic CreateTask model"""
        # Safely derive timestamps if they're not provided on the Pydantic model
        created_at = getattr(task, "created_at", None) or datetime.now()
        updated_at = getattr(task, "updated_at", None) or datetime.now()
        return cls(
            title=task.title,
            description=task.description,
            status=extract_enum_value(task.status),
            priority=extract_enum_value(task.priority),
            assignee=task.assignee if isinstance(task.assignee, str) else task.assignee.value,
            created_at=created_at,
            updated_at=updated_at,
            created_by=task.created_by or "unknown",
            updated_by=task.updated_by or task.created_by or "unknown",
            due_date=task.due_date
        )

    def to_dict(self) -> dict:
        """Convert TaskTable instance to dictionary for Pydantic Task model"""
        return {
            "task_id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assignee": self.assignee,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "due_date": self.due_date,
        }

