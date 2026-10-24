from datetime import date, datetime, timedelta, timezone

from domain.enums import TaskPriority, TaskStatus
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
from domain.value_objects.schedule import Schedule


def test_status_and_inbox_specifications(task_factory):
    planned = task_factory()
    archived = task_factory(2, status=TaskStatus.COMPLETED)

    assert PendingTasks().is_satisfied_by(planned)
    assert InboxTasks().is_satisfied_by(planned)
    assert ArchivedTasks().is_satisfied_by(archived)
    assert TasksWithStatus(TaskStatus.COMPLETED).is_satisfied_by(archived)


def test_schedule_specifications_match_supported_schedule(task_factory):
    start = datetime(2026, 1, 15, 12, tzinfo=timezone.utc)
    end = start + timedelta(hours=2)
    task = task_factory(schedule=Schedule(start_at=start, end_at=end))

    assert ScheduledOn(date(2026, 1, 15)).is_satisfied_by(task)
    assert ScheduledBetween(date(2026, 1, 14), date(2026, 1, 15)).is_satisfied_by(task)


def test_text_and_priority_specifications(task_factory):
    task = task_factory(title="Важлива покупка", priority=TaskPriority.HIGH)

    assert TitleContains("  ПОКУПКА ").is_satisfied_by(task)
    assert MinPriority(TaskPriority.MEDIUM).is_satisfied_by(task)
