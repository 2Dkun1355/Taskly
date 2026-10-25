from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional

from application.common import Handler
from application.interfaces import TaskSearchCriteria, UnitOfWork
from domain.entities.task import Task
from domain.enums import TaskPriority, TaskStatus


class TaskSection(StrEnum):
    """Розділ списку завдань."""

    ALL_ACTIVE = "all_active"
    TODAY = "today"
    UPCOMING = "upcoming"
    ARCHIVE = "archive"


@dataclass(frozen=True)
class ListTasksQuery:
    """Параметри вибірки завдань."""

    section: TaskSection = TaskSection.ALL_ACTIVE
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


@dataclass(frozen=True)
class ListTasksResult:
    """Результат отримання списку завдань."""

    tasks: tuple[Task, ...]


class ListTasksHandler(Handler[ListTasksQuery, ListTasksResult]):
    """Повертає завдання відповідно до параметрів запиту."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def execute(self, command: ListTasksQuery) -> ListTasksResult:
        with self._unit_of_work as uow:
            criteria = self.build_search_criteria(command)
            tasks = uow.tasks.search(criteria)

            if TaskSection(command.section) is TaskSection.ARCHIVE:
                tasks.sort(key=lambda task: task.updated_at, reverse=True)
            else:
                tasks.sort(key=self._sort_key)

            return ListTasksResult(tasks=tuple(tasks))

    @staticmethod
    def build_search_criteria(query: ListTasksQuery) -> TaskSearchCriteria:
        """Перетворює параметри списку на storage-independent критерії."""
        section = TaskSection(query.section)
        now = datetime.now().astimezone()

        if section is TaskSection.ARCHIVE:
            statuses = frozenset(
                {query.status}
                if query.status is not None
                else {
                    TaskStatus.COMPLETED,
                    TaskStatus.NOT_COMPLETED,
                    TaskStatus.CANCELLED,
                }
            )
            return TaskSearchCriteria(
                statuses=statuses,
                priority=query.priority,
            )

        criteria = TaskSearchCriteria(
            statuses=frozenset({TaskStatus.PLANNED}),
            priority=query.priority,
        )
        if section is TaskSection.TODAY:
            return TaskSearchCriteria(
                statuses=criteria.statuses,
                priority=criteria.priority,
                scheduled_on=now.date(),
            )
        if section is TaskSection.UPCOMING:
            return TaskSearchCriteria(
                statuses=criteria.statuses,
                priority=criteria.priority,
                scheduled_after=now.date(),
            )
        return criteria

    @staticmethod
    def _sort_key(task: Task):
        due = task.schedule.end_at or task.schedule.start_at
        return (
            due is None,
            due.timestamp() if due is not None else 0.0,
            -task.priority,
            task.title.value.casefold(),
        )
