from dataclasses import dataclass

from application.interfaces.unit_of_work import UnitOfWork
from application.use_cases.base import Handler
from domain.value_objects.identifiers import TaskId


@dataclass(frozen=True)
class DeleteTaskCommand:
    task_id: str


@dataclass(frozen=True)
class DeleteTaskResult:
    id: str


class DeleteTaskHandler(Handler[DeleteTaskCommand, DeleteTaskResult]):
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def handle(self, command: DeleteTaskCommand) -> DeleteTaskResult:
        task_id = TaskId(command.task_id)

        with self._uow as uow:
            uow.tasks.delete(task_id)
            uow.commit()

        return DeleteTaskResult(id=str(task_id))