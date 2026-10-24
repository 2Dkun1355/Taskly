from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, tzinfo

from application.common import Handler
from application.interfaces import UnitOfWork
from application.queries.task_list_enums import ArchiveFilter, TaskSection
from domain.entities.task import Task
from domain.enums import TaskPriority, TaskStatus
from domain.specifications.base import Specification
from domain.specifications.task_specifications import (
    ArchivedTasks,
    InboxTasks,
    MinPriority,
    PendingTasks,
    ScheduledBetween,
    ScheduledOn,
    TasksWithStatus,
    TitleContains,
)


@dataclass(frozen=True)
class ListTasksQuery:
    """Параметри вибірки завдань."""

    section: TaskSection = TaskSection.ALL
    search: str = ""
    archive_filter: ArchiveFilter = ArchiveFilter.ALL
    min_priority: str | None = None
    client_timezone: tzinfo = timezone.utc


@dataclass(frozen=True)
class ListTasksResult:
    """Результат отримання списку завдань."""

    tasks: tuple[Task, ...]
    counts: dict[TaskSection, int]


class TaskListSpecificationFactory:
    """Будує специфікацію для вибірки завдань."""

    @staticmethod
    def create(command: ListTasksQuery) -> Specification:
        section = TaskSection(command.section)
        archive_filter = ArchiveFilter(command.archive_filter)
        now = datetime.now(timezone.utc).astimezone(command.client_timezone)

        specifications = {
            TaskSection.TODAY: (
                PendingTasks()
                & ScheduledOn(now.date(), command.client_timezone)
            ),
            TaskSection.UPCOMING: (
                PendingTasks()
                & ScheduledBetween(
                    now.date() + timedelta(days=1),
                    now.date() + timedelta(days=7),
                    command.client_timezone,
                )
            ),
            TaskSection.INBOX: InboxTasks(),
            TaskSection.ARCHIVE: ArchivedTasks(),
        }
        specification = specifications.get(section, PendingTasks())

        if archive_filter is not ArchiveFilter.ALL:
            specification &= TasksWithStatus(TaskStatus(archive_filter.value))
        if command.search.strip():
            specification &= TitleContains(command.search)
        if command.min_priority is not None:
            specification &= MinPriority(TaskPriority[command.min_priority])

        return specification


class ListTasksHandler(Handler[ListTasksQuery, ListTasksResult]):
    """Повертає завдання відповідно до параметрів запиту."""

    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def execute(self, command: ListTasksQuery) -> ListTasksResult:
        with self._unit_of_work as uow:
            specification = TaskListSpecificationFactory.create(command)
            all_tasks = uow.tasks.get_all()
            tasks = [
                task for task in all_tasks
                if specification.is_satisfied_by(task)
            ]

            if TaskSection(command.section) is TaskSection.ARCHIVE:
                tasks.sort(key=lambda task: task.updated_at, reverse=True)
            else:
                tasks.sort(key=self._sort_key)

            counts = {}
            for section in TaskSection:
                section_specification = TaskListSpecificationFactory.create(
                    ListTasksQuery(
                        section=section,
                        client_timezone=command.client_timezone,
                    )
                )
                counts[section] = sum(
                    section_specification.is_satisfied_by(task)
                    for task in all_tasks
                )

            return ListTasksResult(
                tasks=tuple(tasks),
                counts=counts,
            )

    @staticmethod
    def _sort_key(task: Task):
        due = task.schedule.end_at or task.schedule.start_at
        return (
            due is None,
            due.timestamp() if due is not None else 0.0,
            -task.priority,
            task.title.value.casefold(),
        )
