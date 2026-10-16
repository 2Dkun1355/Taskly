from datetime import date, datetime, timedelta, timezone

import pytest

from domain.entities.task import Task
from domain.enums import TaskPriority
from domain.exceptions import ValidationException
from domain.specifications.base import Specification
from domain.specifications.task_specifications import (
    ArchivedTasks,
    InboxTasks,
    MinPriority,
    OverdueTasks,
    PendingTasks,
    ScheduledBetween,
    ScheduledOn,
    TitleContains,
)
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title


UTC = timezone.utc
NOW = datetime(2026, 5, 10, 12, tzinfo=UTC)


def make_task(
    title="Купити молоко",
    priority=TaskPriority.LOW,
    schedule=None,
):
    return Task.create(
        title=Title(title),
        now=NOW,
        priority=priority,
        schedule=schedule,
    )


def test_pending_tasks_matches_planned_task():
    assert PendingTasks().is_satisfied_by(make_task())


def test_archived_tasks_matches_completed_task():
    task = make_task()
    task.complete(NOW + timedelta(minutes=1))

    assert ArchivedTasks().is_satisfied_by(task)


def test_inbox_tasks_matches_task_without_dates():
    assert InboxTasks().is_satisfied_by(make_task())


def test_inbox_tasks_rejects_task_with_schedule():
    schedule = Schedule(start_at=NOW + timedelta(hours=1))
    assert not InboxTasks().is_satisfied_by(make_task(schedule=schedule))


def test_overdue_tasks_matches_past_deadline():
    task = make_task(schedule=Schedule(end_at=NOW - timedelta(minutes=1)))

    assert OverdueTasks(NOW).is_satisfied_by(task)


def test_overdue_tasks_rejects_future_deadline():
    task = make_task(schedule=Schedule(end_at=NOW + timedelta(minutes=1)))

    assert not OverdueTasks(NOW).is_satisfied_by(task)


def test_overdue_tasks_rejects_archived_task():
    task = make_task(schedule=Schedule(end_at=NOW - timedelta(minutes=1)))
    task.complete(NOW)

    assert not OverdueTasks(NOW).is_satisfied_by(task)


def test_scheduled_on_matches_interval_overlapping_day():
    schedule = Schedule(
        start_at=datetime(2026, 5, 9, 23, tzinfo=UTC),
        end_at=datetime(2026, 5, 10, 2, tzinfo=UTC),
    )
    task = make_task(schedule=schedule)

    assert ScheduledOn(date(2026, 5, 10)).is_satisfied_by(task)


def test_scheduled_on_matches_start_only():
    task = make_task(
        schedule=Schedule(start_at=datetime(2026, 5, 10, 14, tzinfo=UTC))
    )

    assert ScheduledOn(date(2026, 5, 10)).is_satisfied_by(task)


def test_scheduled_on_matches_deadline_only():
    task = make_task(
        schedule=Schedule(end_at=datetime(2026, 5, 10, 14, tzinfo=UTC))
    )

    assert ScheduledOn(date(2026, 5, 10)).is_satisfied_by(task)


def test_scheduled_on_rejects_task_without_dates():
    assert not ScheduledOn(date(2026, 5, 10)).is_satisfied_by(make_task())


def test_scheduled_between_includes_both_boundary_days():
    task = make_task(
        schedule=Schedule(
            start_at=datetime(2026, 5, 8, 23, tzinfo=UTC),
            end_at=datetime(2026, 5, 12, 1, tzinfo=UTC),
        )
    )

    assert ScheduledBetween(date(2026, 5, 9), date(2026, 5, 11)).is_satisfied_by(task)


def test_scheduled_between_rejects_reversed_dates():
    with pytest.raises(ValidationException):
        ScheduledBetween(date(2026, 5, 12), date(2026, 5, 9))


def test_title_contains_ignores_case():
    assert TitleContains("МОЛОКО").is_satisfied_by(make_task())


def test_title_contains_strips_search_text():
    assert TitleContains("  молоко  ").is_satisfied_by(make_task())


def test_title_contains_rejects_nonmatching_text():
    assert not TitleContains("хліб").is_satisfied_by(make_task())


def test_min_priority_matches_equal_or_higher_priority():
    assert MinPriority(TaskPriority.MEDIUM).is_satisfied_by(
        make_task(priority=TaskPriority.MEDIUM)
    )
    assert MinPriority(TaskPriority.MEDIUM).is_satisfied_by(
        make_task(priority=TaskPriority.HIGH)
    )


def test_min_priority_rejects_lower_priority():
    assert not MinPriority(TaskPriority.MEDIUM).is_satisfied_by(
        make_task(priority=TaskPriority.LOW)
    )


def test_specifications_can_be_combined_with_and_or_not():
    task = make_task(title="Купити молоко", priority=TaskPriority.HIGH)

    assert (
        TitleContains("молоко") & MinPriority(TaskPriority.MEDIUM)
    ).is_satisfied_by(task)

    assert (
        TitleContains("хліб") | MinPriority(TaskPriority.HIGH)
    ).is_satisfied_by(task)

    assert (~TitleContains("хліб")).is_satisfied_by(task)


def test_custom_specification_can_be_implemented():
    class AlwaysTrue(Specification):
        def is_satisfied_by(self, task: Task) -> bool:
            return True

    assert AlwaysTrue().is_satisfied_by(make_task())