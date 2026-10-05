from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional

from application.interfaces.unit_of_work import UnitOfWork
from application.use_cases.base import Command, Handler
from domain.entities.task import Task
from domain.enums.task_status import TaskStatus
from domain.exceptions import ValidationException
from domain.value_objects.identifiers import TaskId
from domain.value_objects.schedule import Schedule


@dataclass(frozen=True)
class ChangeTaskStatusResult:
    id: str
    status: TaskStatus
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    completed_at: Optional[datetime]
    updated_at: datetime


@dataclass(frozen=True)
class ChangeTaskStatusCommand(Command[ChangeTaskStatusResult]):
    task_id: str
    status: TaskStatus
    start_at: Optional[datetime] = None  # used only when restarting (status=PENDING)
    end_at: Optional[datetime] = None


class ChangeTaskStatusHandler(Handler[ChangeTaskStatusCommand, ChangeTaskStatusResult]):
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        self._transitions: dict[TaskStatus, Callable[[Task, ChangeTaskStatusCommand], None]] = {
            TaskStatus.COMPLETED: lambda task, command: task.complete(),
            TaskStatus.CANCELLED: lambda task, command: task.cancel(),
            TaskStatus.PENDING: self._restart,
        }

    def handle(self, command: ChangeTaskStatusCommand) -> ChangeTaskStatusResult:
        transition = self._transitions.get(command.status)
        if transition is None:
            raise ValidationException(f"Unsupported target status '{command.status}'")

        with self._uow as uow:
            task = uow.tasks.get(TaskId(command.task_id))
            transition(task, command)
            uow.tasks.save(task)
            uow.commit()

        return ChangeTaskStatusResult(
            id=str(task.id),
            status=task.status,
            start_at=task.schedule.start_at,
            end_at=task.schedule.end_at,
            completed_at=task.completed_at,
            updated_at=task.updated_at,
        )

    @staticmethod
    def _restart(task: Task, command: ChangeTaskStatusCommand):
        task.restart(Schedule(start_at=command.start_at, end_at=command.end_at))