from datetime import date, datetime, time, timedelta, timezone, tzinfo

from domain.entities.task import Task
from domain.enums import TaskPriority
from domain.exceptions import ValidationException
from domain.specifications.base import Specification


def _day_bounds(day: date, tz: tzinfo):
    """Повертає межі дня в UTC."""
    start = datetime.combine(day, time.min, tzinfo=tz)
    end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=tz)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def _schedule_intersects(task: Task, start: datetime, end: datetime) -> bool:
    """Перевіряє перетин розкладу завдання з часовим діапазоном."""
    schedule = task.schedule
    task_start = schedule.start_at
    task_end = schedule.end_at

    if task_start is not None and task_end is not None:
        return task_start < end and task_end > start

    if task_start is not None:
        return start <= task_start < end

    if task_end is not None:
        return start <= task_end < end

    return False


class PendingTasks(Specification):
    """Заплановані завдання."""

    def is_satisfied_by(self, task: Task) -> bool:
        """Перевіряє статус завдання."""
        return task.is_planned


class ArchivedTasks(Specification):
    """Завдання в архіві."""

    def is_satisfied_by(self, task: Task) -> bool:
        """Перевіряє, чи завдання перебуває в архіві."""
        return task.is_archived


class InboxTasks(Specification):
    """Заплановані завдання без дат."""

    def is_satisfied_by(self, task: Task) -> bool:
        """Перевіряє, чи завдання належить до вхідних."""
        return task.is_in_inbox


class OverdueTasks(Specification):
    """Заплановані завдання з минулим дедлайном."""

    def __init__(self, now: datetime):
        self._now = now

    def is_satisfied_by(self, task: Task) -> bool:
        """Перевіряє, чи минув дедлайн завдання."""
        return (
            task.is_planned
            and task.schedule.end_at is not None
            and task.schedule.end_at < self._now
        )


class ScheduledOn(Specification):
    """Завдання, розклад яких перетинається з указаним днем."""

    def __init__(self, day: date, tz: tzinfo = timezone.utc):
        self._start, self._end = _day_bounds(day, tz)

    def is_satisfied_by(self, task: Task) -> bool:
        """Перевіряє розклад на вказаний день."""
        return _schedule_intersects(task, self._start, self._end)


class ScheduledBetween(Specification):
    """Завдання, розклад яких перетинається з указаним діапазоном днів."""

    def __init__(
        self,
        first: date,
        last: date,
        tz: tzinfo = timezone.utc,
    ):
        if first > last:
            raise ValidationException(
                "Початкова дата не може бути пізнішою за кінцеву"
            )

        self._start, _ = _day_bounds(first, tz)
        _, self._end = _day_bounds(last, tz)

    def is_satisfied_by(self, task: Task) -> bool:
        """Перевіряє розклад у межах указаних днів."""
        return _schedule_intersects(task, self._start, self._end)


class TitleContains(Specification):
    """Завдання, назва яких містить указаний текст."""

    def __init__(self, text: str):
        self._text = text.strip().casefold()

    def is_satisfied_by(self, task: Task) -> bool:
        """Перевіряє назву без урахування регістру."""
        return self._text in task.title.value.casefold()


class MinPriority(Specification):
    """Завдання з указаним або вищим пріоритетом."""

    def __init__(self, priority: TaskPriority):
        self._priority = priority

    def is_satisfied_by(self, task: Task) -> bool:
        """Перевіряє рівень пріоритету."""
        return task.priority >= self._priority
