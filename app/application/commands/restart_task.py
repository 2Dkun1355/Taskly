from dataclasses import dataclass
from datetime import datetime

from domain.exceptions import InvalidTaskException
from domain.value_objects.identifiers import TaskId
from application.common import Handler
from application.interfaces import UnitOfWork


@dataclass(frozen=True)
class RestartTaskCommand:
    """Ідентифікатор завдання для перезапуску."""

    task_id: TaskId


@dataclass(frozen=True)
class RestartTaskResult:
    """Результат перезапуску завдання."""

    task_id: TaskId


class RestartTaskHandler(Handler[RestartTaskCommand, RestartTaskResult]):
    """Повертає архівне завдання до запланованого стану."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def execute(self, command: RestartTaskCommand) -> RestartTaskResult:
        now = datetime.now().astimezone()

        with self._unit_of_work as uow:
            task = uow.tasks.get_by_id(command.task_id)

            if task is None:
                raise InvalidTaskException("Завдання не знайдено")

            task.restart(now)
            uow.tasks.update(task)
            uow.commit()

        return RestartTaskResult(task_id=task.id)
