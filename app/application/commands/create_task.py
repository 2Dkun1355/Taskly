from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.entities.task import Task
from domain.enums import TaskPriority
from domain.value_objects.identifiers import TaskId
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title
from application.common import Handler
from application.interfaces import UnitOfWork


@dataclass(frozen=True)
class CreateTaskCommand:
    """Дані для створення завдання."""

    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.LOW
    schedule: Optional[Schedule] = None


@dataclass(frozen=True)
class CreateTaskResult:
    """Результат створення завдання."""

    task_id: TaskId


class CreateTaskHandler(Handler[CreateTaskCommand, CreateTaskResult]):
    """Створює та зберігає завдання."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def execute(self, command: CreateTaskCommand) -> CreateTaskResult:
        now = datetime.now().astimezone()
        task = Task.create(
            title=Title(command.title),
            now=now,
            description=command.description,
            priority=command.priority,
            schedule=command.schedule,
        )

        with self._unit_of_work as uow:
            uow.tasks.add(task)
            uow.commit()

        return CreateTaskResult(task_id=task.id)
