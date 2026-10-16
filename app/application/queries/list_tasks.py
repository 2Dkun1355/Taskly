from dataclasses import dataclass

from domain.entities.task import Task
from application.common import Handler
from application.interfaces import UnitOfWork


@dataclass(frozen=True)
class ListTasksQuery:
    """Запит усіх завдань."""


@dataclass(frozen=True)
class ListTasksResult:
    """Результат отримання списку завдань."""

    tasks: tuple[Task, ...]


class ListTasksHandler(Handler[ListTasksQuery, ListTasksResult]):
    """Повертає всі завдання."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def execute(self, command: ListTasksQuery) -> ListTasksResult:
        with self._unit_of_work as uow:
            tasks = uow.tasks.get_all()
            return ListTasksResult(tasks=tuple(tasks))
