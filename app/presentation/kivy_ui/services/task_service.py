from datetime import datetime

from application.commands.cancel_task import CancelTaskCommand
from application.commands.complete_task import CompleteTaskCommand
from application.commands.create_task import CreateTaskCommand
from application.commands.delete_task import DeleteTaskCommand
from application.commands.edit_task import EditTaskCommand
from application.commands.mark_task_not_completed import MarkTaskNotCompletedCommand
from application.commands.restart_task import RestartTaskCommand
from application.queries.list_tasks import ListTasksQuery
from application.queries.task_list_enums import ArchiveFilter, TaskSection

SECTION_TODAY = TaskSection.TODAY
SECTION_UPCOMING = TaskSection.UPCOMING
SECTION_INBOX = TaskSection.INBOX
SECTION_ALL = TaskSection.ALL
SECTION_ARCHIVE = TaskSection.ARCHIVE

# Основні розділи бічного меню, зверху вниз.
SECTIONS = (
    (TaskSection.ALL, TaskSection.ALL.label),
    (TaskSection.TODAY, TaskSection.TODAY.label),
    (TaskSection.UPCOMING, TaskSection.UPCOMING.label),
    (TaskSection.INBOX, TaskSection.INBOX.label),
)

# Архів показується окремо, в самому низу меню.
ARCHIVE_SECTION = (TaskSection.ARCHIVE, TaskSection.ARCHIVE.label)

class TaskService:
    """Усе, що потрібно інтерфейсу від прикладного шару."""

    def __init__(self, mediator):
        self._mediator = mediator

    # Читання

    def select(
        self, section, search="", archive_filter=ArchiveFilter.ALL, min_priority=None
    ):
        return self._mediator.send(
            ListTasksQuery(
                section=TaskSection(section),
                search=search,
                archive_filter=ArchiveFilter(archive_filter),
                min_priority=min_priority,
                client_timezone=datetime.now().astimezone().tzinfo,
            )
        )

    @staticmethod
    def state_of(task):
        """Стан для показу: inbox, planned, completed, not_completed, cancelled."""
        if task.is_planned:
            if task.is_in_inbox:
                return "inbox"
            return "planned"
        return task.status.name.lower()

    # Дії

    def create_task(self, title, description, priority, start_at, end_at):
        """Створює завдання. Дати вже повинні бути з часовим поясом або None."""
        return self._mediator.send(
            CreateTaskCommand(
                title=title,
                description=description,
                priority=priority,
                start_at=start_at,
                end_at=end_at,
            )
        )

    def edit_task(self, task, title, description, priority, start_at, end_at):
        """Змінює назву, опис, пріоритет і розклад завдання."""
        return self._mediator.send(
            EditTaskCommand(
                task_id=task.id,
                title=title,
                description=description,
                priority=priority,
                start_at=start_at,
                end_at=end_at,
            )
        )

    def complete(self, task):
        return self._mediator.send(CompleteTaskCommand(task_id=task.id))

    def mark_not_completed(self, task):
        return self._mediator.send(MarkTaskNotCompletedCommand(task_id=task.id))

    def cancel(self, task):
        return self._mediator.send(CancelTaskCommand(task_id=task.id))

    def restart(self, task):
        return self._mediator.send(RestartTaskCommand(task_id=task.id))

    def delete(self, task):
        """Видаляє завдання назавжди."""
        return self._mediator.send(DeleteTaskCommand(task_id=task.id))
