from dataclasses import dataclass

from domain.value_objects.identifiers import TaskId
from application.common import Handler
from application.interfaces import UnitOfWork


@dataclass(frozen=True)
class DeleteTaskCommand:
    """Дані для видалення завдання."""

    task_id: TaskId


class DeleteTaskHandler(Handler[DeleteTaskCommand, None]):
    """Видаляє завдання за ідентифікатором."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def execute(self, command: DeleteTaskCommand):
        with self._unit_of_work as uow:
            uow.tasks.delete(command.task_id)
            uow.commit()