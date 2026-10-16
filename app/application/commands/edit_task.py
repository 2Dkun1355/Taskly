from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.enums import TaskPriority
from domain.exceptions import InvalidTaskException
from domain.value_objects.identifiers import TaskId
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title
from application.common import Handler
from application.interfaces import UnitOfWork


@dataclass(frozen=True)
class EditTaskCommand:
    """Дані для редагування завдання."""

    task_id: TaskId
    title: str
    description: Optional[str]
    priority: TaskPriority
    schedule: Schedule


@dataclass(frozen=True)
class EditTaskResult:
    """Результат редагування завдання."""

    task_id: TaskId


class EditTaskHandler(Handler[EditTaskCommand, EditTaskResult]):
    """Редагує та зберігає завдання."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def execute(self, command: EditTaskCommand) -> EditTaskResult:
        now = datetime.now().astimezone()

        with self._unit_of_work as uow:
            task = uow.tasks.get_by_id(command.task_id)

            if task is None:
                raise InvalidTaskException("Завдання не знайдено")

            task.edit(
                title=Title(command.title),
                description=command.description,
                priority=command.priority,
                schedule=command.schedule,
                now=now,
            )
            uow.tasks.update(task)
            uow.commit()

        return EditTaskResult(task_id=task.id)
