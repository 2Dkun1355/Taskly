from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from application.interfaces.unit_of_work import UnitOfWork
from application.use_cases.base import Handler
from domain.entities.task import Task
from domain.enums.task_priority import TaskPriority
from domain.enums.task_status import TaskStatus
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title


@dataclass(frozen=True)
class CreateTaskCommand:
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


@dataclass(frozen=True)
class CreateTaskResult:
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    created_at: datetime


class CreateTaskHandler(Handler[CreateTaskCommand, CreateTaskResult]):
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def handle(self, command: CreateTaskCommand) -> CreateTaskResult:
        task = Task.create(
            title=Title(command.title),
            description=command.description,
            priority=command.priority,
            schedule=Schedule(start_at=command.start_at, end_at=command.end_at),
        )

        with self._uow as uow:
            uow.tasks.add(task)
            uow.commit()

        return CreateTaskResult(
            id=str(task.id),
            title=str(task.title),
            description=task.description,
            status=task.status,
            priority=task.priority,
            start_at=task.schedule.start_at,
            end_at=task.schedule.end_at,
            created_at=task.created_at,
        )