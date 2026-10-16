from dataclasses import dataclass

from domain.entities.task import Task
from domain.exceptions import InvalidTaskException
from domain.value_objects.identifiers import TaskId
from application.common import Handler
from application.interfaces import UnitOfWork


@dataclass(frozen=True)
class GetTaskQuery:
    """Ідентифікатор завдання для пошуку."""

    task_id: TaskId


@dataclass(frozen=True)
class GetTaskResult:
    """Результат пошуку завдання."""

    task: Task


class GetTaskHandler(Handler[GetTaskQuery, GetTaskResult]):
    """Знаходить завдання за ідентифікатором."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def execute(self, command: GetTaskQuery) -> GetTaskResult:
        with self._unit_of_work as uow:
            task = uow.tasks.get_by_id(command.task_id)

            if task is None:
                raise InvalidTaskException("Завдання не знайдено")

            return GetTaskResult(task=task)
