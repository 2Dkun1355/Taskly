from datetime import datetime, timedelta

from application.commands.cancel_task import CancelTaskCommand
from application.commands.complete_task import CompleteTaskCommand
from application.commands.create_task import CreateTaskCommand
from application.commands.delete_task import DeleteTaskCommand
from application.commands.edit_task import EditTaskCommand
from application.commands.mark_task_not_completed import MarkTaskNotCompletedCommand
from application.commands.restart_task import RestartTaskCommand
from application.queries.list_tasks import ListTasksQuery
from domain.enums import TaskPriority
from domain.specifications.task_specifications import (
    ArchivedTasks,
    InboxTasks,
    OverdueTasks,
    PendingTasks,
    ScheduledOn,
    TitleContains,
)
from domain.value_objects.schedule import Schedule

SECTION_TODAY = "today"
SECTION_TOMORROW = "tomorrow"
SECTION_LATER = "later"
SECTION_INBOX = "inbox"
SECTION_ALL = "all"
SECTION_ARCHIVE = "archive"

# Основні розділи бічного меню, зверху вниз.
SECTIONS = (
    (SECTION_TODAY, "Сьогодні"),
    (SECTION_TOMORROW, "Завтра"),
    (SECTION_LATER, "Майбутні"),
    (SECTION_INBOX, "Без дати"),
    (SECTION_ALL, "Усі завдання"),
)

# Архів показується окремо, в самому низу меню.
ARCHIVE_SECTION = (SECTION_ARCHIVE, "Архів")

_PRIORITY_RANK = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}


def _active_sort_key(task):
    """Спершу найближчі терміни, потім вищий пріоритет, потім за назвою."""
    due = task.schedule.end_at or task.schedule.start_at
    return (
        due is None,
        due.timestamp() if due is not None else 0.0,
        -_PRIORITY_RANK.get(task.priority.name, 0),
        task.title.value.casefold(),
    )


class TaskService:
    """Усе, що потрібно інтерфейсу від прикладного шару."""

    def __init__(self, mediator):
        self._mediator = mediator

    # Читання

    def load_tasks(self):
        """Завантажує всі завдання."""
        result = self._mediator.send(ListTasksQuery())
        return list(result.tasks)

    def select(self, tasks, section, search=""):
        """Відбирає й сортує завдання розділу, за потреби з пошуком за назвою."""
        belongs = self._section_filter(section)
        matches_search = (
            TitleContains(search).is_satisfied_by
            if search.strip() else (lambda task: True)
        )

        selected = [
            task for task in tasks
            if belongs(task) and matches_search(task)
        ]

        if section == SECTION_ARCHIVE:
            return sorted(selected, key=lambda task: task.updated_at, reverse=True)
        return sorted(selected, key=_active_sort_key)

    def count(self, tasks, section):
        """Кількість завдань у розділі."""
        belongs = self._section_filter(section)
        return sum(1 for task in tasks if belongs(task))

    @staticmethod
    def state_of(task):
        """Стан для показу: inbox, overdue, planned, completed, not_completed, cancelled."""
        if task.is_planned:
            if task.is_in_inbox:
                return "inbox"
            if OverdueTasks(datetime.now().astimezone()).is_satisfied_by(task):
                return "overdue"
            return "planned"
        return task.status.name.lower()

    # Дії

    def create_task(self, title, description, priority, start_at, end_at):
        """Створює завдання. Дати вже повинні бути з часовим поясом або None."""
        return self._mediator.send(
            CreateTaskCommand(
                title=title,
                description=description or None,
                priority=TaskPriority[priority],
                schedule=Schedule(start_at=start_at, end_at=end_at),
            )
        )

    def edit_task(self, task, title, description, priority, start_at, end_at):
        """Змінює назву, опис, пріоритет і розклад завдання."""
        return self._mediator.send(
            EditTaskCommand(
                task_id=task.id,
                title=title,
                description=description or None,
                priority=TaskPriority[priority],
                schedule=Schedule(start_at=start_at, end_at=end_at),
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

    # Допоміжне

    @staticmethod
    def _section_filter(section):
        """Повертає функцію, що каже, чи належить завдання розділу.

        «Сьогодні» і «Завтра» рахуються за локальною добою. «Майбутні» це
        заплановані завдання з датою, які не припадають ні на сьогодні, ні на завтра.
        """
        local_now = datetime.now().astimezone()
        today = local_now.date()
        tz = local_now.tzinfo

        on_today = ScheduledOn(today, tz)
        on_tomorrow = ScheduledOn(today + timedelta(days=1), tz)

        if section == SECTION_TODAY:
            return (PendingTasks() & on_today).is_satisfied_by
        if section == SECTION_TOMORROW:
            return (PendingTasks() & on_tomorrow).is_satisfied_by
        if section == SECTION_LATER:
            def is_other_term(task):
                return (
                    task.is_planned
                    and not task.is_in_inbox
                    and not on_today.is_satisfied_by(task)
                    and not on_tomorrow.is_satisfied_by(task)
                )
            return is_other_term
        if section == SECTION_INBOX:
            return InboxTasks().is_satisfied_by
        if section == SECTION_ARCHIVE:
            return ArchivedTasks().is_satisfied_by
        return PendingTasks().is_satisfied_by