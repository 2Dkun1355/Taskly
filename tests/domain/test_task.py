from datetime import datetime, timedelta, timezone

import pytest

from domain.entities.task import MAX_DESCRIPTION_LENGTH, Task
from domain.enums import TaskPriority, TaskStatus
from domain.exceptions import InvalidTaskException, ValidationException
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title


NOW = datetime(2026, 5, 1, 12, tzinfo=timezone.utc)


def make_task(**kwargs):
    return Task.create(title=Title("Тестове завдання"), now=NOW, **kwargs)


def test_create_uses_expected_defaults():
    task = make_task()

    assert task.status is TaskStatus.PLANNED
    assert task.priority is TaskPriority.LOW
    assert task.schedule == Schedule()
    assert task.completed_at is None
    assert task.created_at == NOW
    assert task.updated_at == NOW


def test_create_normalizes_description():
    task = make_task(description="  опис завдання  ")
    assert task.description == "опис завдання"


@pytest.mark.parametrize("description", ["", "   ", "\n\t"])
def test_create_converts_empty_description_to_none(description):
    assert make_task(description=description).description is None


def test_create_rejects_non_string_description():
    with pytest.raises(ValidationException):
        make_task(description=123)


def test_create_rejects_description_over_limit():
    with pytest.raises(ValidationException):
        make_task(description="x" * (MAX_DESCRIPTION_LENGTH + 1))


def test_task_state_properties():
    task = make_task()

    assert task.is_planned
    assert not task.is_archived
    assert task.is_in_inbox


def test_edit_changes_task_fields():
    task = make_task()
    new_schedule = Schedule(
        start_at=NOW + timedelta(hours=1),
        end_at=NOW + timedelta(hours=2),
    )
    updated_at = NOW + timedelta(minutes=5)

    task.edit(
        title=Title("Нова назва"),
        description="  новий опис  ",
        priority=TaskPriority.HIGH,
        schedule=new_schedule,
        now=updated_at,
    )

    assert task.title == Title("Нова назва")
    assert task.description == "новий опис"
    assert task.priority is TaskPriority.HIGH
    assert task.schedule == new_schedule
    assert task.updated_at == updated_at


def test_edit_rejects_archived_task():
    task = make_task()
    task.complete(NOW + timedelta(minutes=1))

    with pytest.raises(InvalidTaskException):
        task.edit(
            title=Title("Інша назва"),
            description=None,
            priority=TaskPriority.LOW,
            schedule=Schedule(),
            now=NOW + timedelta(minutes=2),
        )


@pytest.mark.parametrize("description", [123, "x" * (MAX_DESCRIPTION_LENGTH + 1)])
def test_edit_rejects_invalid_description(description):
    task = make_task()

    with pytest.raises(ValidationException):
        task.edit(
            title=Title("Нова назва"),
            description=description,
            priority=TaskPriority.LOW,
            schedule=Schedule(),
            now=NOW + timedelta(minutes=1),
        )


def test_complete_sets_status_and_completion_time():
    task = make_task()
    completed_at = NOW + timedelta(minutes=10)

    task.complete(completed_at)

    assert task.status is TaskStatus.COMPLETED
    assert task.completed_at == completed_at
    assert task.updated_at == completed_at
    assert task.is_archived


def test_complete_rejects_non_planned_task():
    task = make_task()
    task.complete(NOW + timedelta(minutes=1))

    with pytest.raises(InvalidTaskException):
        task.complete(NOW + timedelta(minutes=2))


def test_mark_not_completed_archives_task():
    task = make_task()
    marked_at = NOW + timedelta(minutes=10)

    task.mark_not_completed(marked_at)

    assert task.status is TaskStatus.NOT_COMPLETED
    assert task.completed_at is None
    assert task.is_archived


def test_mark_not_completed_rejects_archived_task():
    task = make_task()
    task.cancel(NOW + timedelta(minutes=1))

    with pytest.raises(InvalidTaskException):
        task.mark_not_completed(NOW + timedelta(minutes=2))


def test_cancel_sets_cancelled_status():
    task = make_task()
    cancelled_at = NOW + timedelta(minutes=10)

    task.cancel(cancelled_at)

    assert task.status is TaskStatus.CANCELLED
    assert task.is_archived
    assert task.updated_at == cancelled_at


def test_cancel_rejects_completed_task():
    task = make_task()
    task.complete(NOW + timedelta(minutes=1))

    with pytest.raises(InvalidTaskException):
        task.cancel(NOW + timedelta(minutes=2))


@pytest.mark.parametrize(
    "archive_action",
    ["complete", "mark_not_completed", "cancel"],
)
def test_restart_returns_archived_task_to_planned(archive_action):
    task = make_task()
    archive_time = NOW + timedelta(minutes=1)
    getattr(task, archive_action)(archive_time)

    task.schedule = Schedule(
        start_at=NOW + timedelta(hours=1),
        end_at=NOW + timedelta(hours=2),
    )
    task.restart(NOW + timedelta(minutes=2))

    assert task.status is TaskStatus.PLANNED
    assert task.schedule == Schedule()
    assert task.completed_at is None
    assert task.updated_at == NOW + timedelta(minutes=2)
    assert task.is_planned


def test_restart_rejects_planned_task():
    task = make_task()

    with pytest.raises(InvalidTaskException):
        task.restart(NOW + timedelta(minutes=1))
