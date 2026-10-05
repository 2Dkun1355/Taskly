from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from application.interfaces.unit_of_work import UnitOfWork
from application.use_cases.base import Command, Handler
from domain.enums.task_priority import TaskPriority
from domain.enums.task_status import TaskStatus
from domain.value_objects.identifiers import TaskId


@dataclass(frozen=True)
class GetTaskResult:
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class GetTaskCommand(Command[GetTaskResult]):
    task_id: str


class GetTaskHandler(Handler[GetTaskCommand, GetTaskResult]):
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def handle(self, command: GetTaskCommand) -> GetTaskResult:
        with self._uow as uow:
            task = uow.tasks.get(TaskId(command.task_id))

        return GetTaskResult(
            id=str(task.id),
            title=str(task.title),
            description=task.description,
            status=task.status,
            priority=task.priority,
            start_at=task.schedule.start_at,
            end_at=task.schedule.end_at,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )