from dataclasses import dataclass
from datetime import datetime, timezone

from domain.exceptions import InvalidTaskException
from domain.value_objects.identifiers import TaskId
from application.common import Handler
from application.interfaces import UnitOfWork


@dataclass(frozen=True)
class MarkTaskNotCompletedCommand:
    """Ідентифікатор завдання для позначення невиконаним."""

    task_id: TaskId


@dataclass(frozen=True)
class MarkTaskNotCompletedResult:
    """Результат позначення завдання невиконаним."""

    task_id: TaskId


class MarkTaskNotCompletedHandler(
    Handler[MarkTaskNotCompletedCommand, MarkTaskNotCompletedResult]
):
    """Позначає завдання невиконаним."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def execute(
        self,
        command: MarkTaskNotCompletedCommand,
    ) -> MarkTaskNotCompletedResult:
        now = datetime.now(timezone.utc)

        with self._unit_of_work as uow:
            task = uow.tasks.get_by_id(command.task_id)

            if task is None:
                raise InvalidTaskException("Завдання не знайдено")

            task.mark_not_completed(now)
            uow.tasks.update(task)
            uow.commit()

        return MarkTaskNotCompletedResult(task_id=task.id)
