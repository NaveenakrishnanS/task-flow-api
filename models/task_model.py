from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

# from enums.enums import TaskAssignee, TaskPriority, TaskStatus

from enum import Enum

from db.model.db_model import TaskTable


class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskAssignee(str, Enum):
    UNASSIGNED = "unassigned"

class CreateTask(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.LOW
    assignee: Optional[str | TaskAssignee] = TaskAssignee.UNASSIGNED    
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    due_date: Optional[date] = None

class Task(CreateTask):
    task_id: int
    created_at: datetime
    updated_at: datetime

    def to_db_model(self) -> TaskTable:
        return TaskTable(
            id=self.task_id,
            title=self.title,
            description=self.description,
            status=self.status.value if isinstance(self.status, Enum) else self.status,
            priority=self.priority.value if isinstance(self.priority, Enum) else self.priority,
            assignee=self.assignee if isinstance(self.assignee, str) else self.assignee.value,
            created_at=self.created_at,
            updated_at=self.updated_at,
            created_by=self.created_by,
            updated_by=self.updated_by,
            due_date=self.due_date
        )

class UpdateTask(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str | TaskAssignee] = None
    updated_by: str 
    due_date: Optional[date] = None

    def to_db_model(self, existing_task: TaskTable) -> TaskTable:
        return TaskTable(
            id=existing_task.id,
            title=self.title if self.title is not None else existing_task.title,
            description=self.description if self.description is not None else existing_task.description,
            status=self.status.value if isinstance(self.status, Enum) else (self.status if self.status is not None else existing_task.status),
            priority=self.priority.value if isinstance(self.priority, Enum) else (self.priority if self.priority is not None else existing_task.priority),
            assignee=self.assignee if isinstance(self.assignee, str) else (self.assignee.value if self.assignee is not None else existing_task.assignee),
            created_at=existing_task.created_at,
            updated_at=datetime.now(),
            created_by=existing_task.created_by,
            updated_by=self.updated_by,
            due_date=self.due_date if self.due_date is not None else existing_task.due_date
        )