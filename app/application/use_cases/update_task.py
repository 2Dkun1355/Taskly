from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from application.interfaces.unit_of_work import UnitOfWork
from application.use_cases.base import Handler
from domain.entities.task import Task
from domain.enums.task_priority import TaskPriority
from domain.enums.task_status import TaskStatus
from domain.value_objects.identifiers import TaskId
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title


@dataclass(frozen=True)
class UpdateTaskCommand:
    task_id: str
    title: str
    description: Optional[str]
    priority: TaskPriority
    start_at: Optional[datetime]
    end_at: Optional[datetime]


@dataclass(frozen=True)
class UpdateTaskResult:
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    updated_at: datetime


class UpdateTaskHandler(Handler[UpdateTaskCommand, UpdateTaskResult]):
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def handle(self, command: UpdateTaskCommand) -> UpdateTaskResult:
        title = Title(command.title)
        schedule = Schedule(start_at=command.start_at, end_at=command.end_at)

        with self._uow as uow:
            task = uow.tasks.get(TaskId(command.task_id))
            task.edit(title, command.description, command.priority)
            task.reschedule(schedule)
            uow.tasks.save(task)
            uow.commit()

        return self._to_result(task)

    @staticmethod
    def _to_result(task: Task) -> UpdateTaskResult:
        return UpdateTaskResult(
            id=str(task.id),
            title=str(task.title),
            description=task.description,
            status=task.status,
            priority=task.priority,
            start_at=task.schedule.start_at,
            end_at=task.schedule.end_at,
            updated_at=task.updated_at,
        )