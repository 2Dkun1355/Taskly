from dataclasses import dataclass

from application.common import Handler
from application.interfaces import UnitOfWork


@dataclass(frozen=True)
class ClearArchiveCommand:
    """Команда для видалення всіх архівних завдань."""


@dataclass(frozen=True)
class ClearArchiveResult:
    """Результат очищення архіву."""

    deleted_count: int


class ClearArchiveHandler(Handler[ClearArchiveCommand, ClearArchiveResult]):
    """Видаляє архівні завдання в межах однієї транзакції."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def execute(self, command: ClearArchiveCommand) -> ClearArchiveResult:
        del command

        with self._unit_of_work as uow:
            deleted_count = uow.tasks.delete_archived()
            uow.commit()

        return ClearArchiveResult(deleted_count=deleted_count)
