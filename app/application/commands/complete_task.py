from dataclasses import dataclass
from datetime import datetime

from domain.exceptions import InvalidTaskException
from domain.value_objects.identifiers import TaskId
from application.common import Handler
from application.interfaces import UnitOfWork


@dataclass(frozen=True)
class CompleteTaskCommand:
    """Ідентифікатор завдання для виконання."""

    task_id: TaskId


@dataclass(frozen=True)
class CompleteTaskResult:
    """Результат виконання завдання."""

    task_id: TaskId


class CompleteTaskHandler(Handler[CompleteTaskCommand, CompleteTaskResult]):
    """Позначає завдання виконаним."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def execute(self, command: CompleteTaskCommand) -> CompleteTaskResult:
        now = datetime.now().astimezone()

        with self._unit_of_work as uow:
            task = uow.tasks.get_by_id(command.task_id)

            if task is None:
                raise InvalidTaskException("Завдання не знайдено")

            task.complete(now)
            uow.tasks.update(task)
            uow.commit()

        return CompleteTaskResult(task_id=task.id)
