from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from domain.entities.task import Task
from domain.enums import TaskPriority
from domain.value_objects.identifiers import TaskId
from domain.value_objects.description import Description
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title
from application.common import Handler
from application.interfaces import UnitOfWork


@dataclass(frozen=True)
class CreateTaskCommand:
    """Дані для створення завдання."""

    title: str
    description: str = ""
    priority: str = "LOW"
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


@dataclass(frozen=True)
class CreateTaskResult:
    """Результат створення завдання."""

    task_id: TaskId


class CreateTaskHandler(Handler[CreateTaskCommand, CreateTaskResult]):
    """Створює та зберігає завдання."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def execute(self, command: CreateTaskCommand) -> CreateTaskResult:
        now = datetime.now(timezone.utc)
        task = Task.create(
            id=TaskId.new(),
            title=Title(command.title),
            now=now,
            description=Description(command.description),
            priority=TaskPriority[command.priority],
            schedule=Schedule(
                start_at=(
                    command.start_at.astimezone(timezone.utc)
                    if command.start_at is not None else None
                ),
                end_at=(
                    command.end_at.astimezone(timezone.utc)
                    if command.end_at is not None else None
                ),
            ),
        )

        with self._unit_of_work as uow:
            uow.tasks.add(task)
            uow.commit()

        return CreateTaskResult(task_id=task.id)
