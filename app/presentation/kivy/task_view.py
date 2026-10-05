from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.enums.task_priority import TaskPriority
from domain.enums.task_status import TaskStatus


@dataclass(frozen=True)
class TaskView:
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    is_overdue: bool


@dataclass(frozen=True)
class TaskData:
    title: str
    description: Optional[str]
    priority: TaskPriority
    start_at: Optional[datetime]
    end_at: Optional[datetime]