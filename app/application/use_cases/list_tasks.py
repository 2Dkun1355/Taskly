from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from application.interfaces.unit_of_work import UnitOfWork
from application.use_cases.base import Command, Handler
from domain.entities.task import Task
from domain.enums.task_priority import TaskPriority
from domain.enums.task_status import TaskStatus

_PRIORITY_RANK = {TaskPriority.HIGH: 0, TaskPriority.MEDIUM: 1, TaskPriority.LOW: 2}
_FAR_FUTURE = datetime.max.replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class TaskItem:
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    completed_at: Optional[datetime]
    is_overdue: bool


@dataclass(frozen=True)
class ListTasksResult:
    tasks: list[TaskItem]


@dataclass(frozen=True)
class ListTasksCommand(Command[ListTasksResult]):
    now: datetime
    status: Optional[TaskStatus] = None
    only_overdue: bool = False


class ListTasksHandler(Handler[ListTasksCommand, ListTasksResult]):
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def handle(self, command: ListTasksCommand) -> ListTasksResult:
        with self._uow as uow:
            tasks = uow.tasks.list_all()

        selected = [task for task in tasks if self._matches(task, command)]
        selected.sort(key=self._sort_key)

        return ListTasksResult(
            tasks=[
                TaskItem(
                    id=str(task.id),
                    title=str(task.title),
                    description=task.description,
                    status=task.status,
                    priority=task.priority,
                    start_at=task.schedule.start_at,
                    end_at=task.schedule.end_at,
                    completed_at=task.completed_at,
                    is_overdue=task.is_overdue(command.now),
                )
                for task in selected
            ]
        )

    @staticmethod
    def _matches(task: Task, command: ListTasksCommand) -> bool:
        if command.status is not None and task.status is not command.status:
            return False
        if command.only_overdue and not task.is_overdue(command.now):
            return False
        return True

    @staticmethod
    def _sort_key(task: Task):
        anchor = task.schedule.start_at or task.schedule.end_at or _FAR_FUTURE
        return anchor, _PRIORITY_RANK[task.priority], task.created_at