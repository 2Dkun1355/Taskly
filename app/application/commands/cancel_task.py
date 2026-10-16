from dataclasses import dataclass
from datetime import datetime

from domain.exceptions import InvalidTaskException
from domain.value_objects.identifiers import TaskId
from application.common import Handler
from application.interfaces import UnitOfWork


@dataclass(frozen=True)
class CancelTaskCommand:
    """Ідентифікатор завдання для скасування."""

    task_id: TaskId


@dataclass(frozen=True)
class CancelTaskResult:
    """Результат скасування завдання."""

    task_id: TaskId


class CancelTaskHandler(Handler[CancelTaskCommand, CancelTaskResult]):
    """Скасовує заплановане завдання."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def execute(self, command: CancelTaskCommand) -> CancelTaskResult:
        now = datetime.now().astimezone()

        with self._unit_of_work as uow:
            task = uow.tasks.get_by_id(command.task_id)

            if task is None:
                raise InvalidTaskException("Завдання не знайдено")

            task.cancel(now)
            uow.tasks.update(task)
            uow.commit()

        return CancelTaskResult(task_id=task.id)
