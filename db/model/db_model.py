from sqlalchemy import Column, Integer, String, DateTime, Date
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TaskTable(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    assignee = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    created_by = Column(String, nullable=False)
    updated_by = Column(String, nullable=False)
    due_date = Column(Date, nullable=True)

    @classmethod
    def from_pydantic(cls, task):
        """Create a TaskTable instance from a Pydantic CreateTask model"""
        from enum import Enum
        # Safely derive timestamps if they're not provided on the Pydantic model
        created_at = getattr(task, "created_at", None) or datetime.now()
        updated_at = getattr(task, "updated_at", None) or datetime.now()
        return cls(
            title=task.title,
            description=task.description,
            status=task.status.value if isinstance(task.status, Enum) else task.status,
            priority=task.priority.value if isinstance(task.priority, Enum) else task.priority,
            assignee=task.assignee if isinstance(task.assignee, str) else task.assignee.value,
            created_at=created_at,
            updated_at=updated_at,
            created_by=task.created_by,
            updated_by=task.updated_by,
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

