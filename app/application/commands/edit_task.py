from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from domain.enums import TaskPriority
from domain.exceptions import InvalidTaskException
from domain.value_objects.identifiers import TaskId
from domain.value_objects.description import Description
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title
from application.common import Handler
from application.interfaces import UnitOfWork


@dataclass(frozen=True)
class EditTaskCommand:
    """Дані для редагування завдання."""

    task_id: TaskId
    title: str
    description: str
    priority: str
    start_at: Optional[datetime]
    end_at: Optional[datetime]


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
                description=Description(command.description),
                priority=TaskPriority[command.priority],
                schedule=Schedule(
                    start_at=(
                        command.start_at.astimezone()
                        if command.start_at is not None else None
                    ),
                    end_at=(
                        command.end_at.astimezone()
                        if command.end_at is not None else None
                    ),
                ),
                now=now,
            )
            uow.tasks.update(task)
            uow.commit()

        return EditTaskResult(task_id=task.id)
