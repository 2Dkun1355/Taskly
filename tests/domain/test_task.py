from datetime import timedelta

import pytest

from domain.enums import TaskPriority, TaskStatus
from domain.exceptions import InvalidTaskException
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title


def test_create_uses_ready_value_objects(sample_task):
    assert sample_task.status is TaskStatus.PLANNED
    assert sample_task.is_planned
    assert sample_task.is_in_inbox


def test_entity_equality_and_hash_use_type_and_id(sample_task, task_factory):
    same_id = task_factory(title="Інша назва")
    assert sample_task == same_id
    assert hash(sample_task) == hash(same_id)
    assert len({sample_task, same_id}) == 1


def test_edit_changes_planned_task(sample_task):
    now = sample_task.updated_at + timedelta(minutes=1)
    sample_task.edit(
        title=Title("Оновлена назва"),
        description=sample_task.description,
        priority=TaskPriority.HIGH,
        schedule=Schedule(end_at=now + timedelta(hours=1)),
        now=now,
    )

    assert sample_task.title == Title("Оновлена назва")
    assert sample_task.priority is TaskPriority.HIGH
    assert sample_task.updated_at == now


@pytest.mark.parametrize(
    "action",
    ["complete", "mark_not_completed", "cancel"],
)
def test_archived_task_cannot_be_changed_by_planned_actions(sample_task, action):
    sample_task.complete(sample_task.updated_at)

    with pytest.raises(InvalidTaskException):
        getattr(sample_task, action)(sample_task.updated_at)


def test_restart_archived_task_clears_schedule_and_completion(sample_task):
    complete_at = sample_task.updated_at + timedelta(minutes=1)
    sample_task.schedule = Schedule(end_at=complete_at + timedelta(hours=1))
    sample_task.complete(complete_at)

    restart_at = complete_at + timedelta(minutes=1)
    sample_task.restart(restart_at)

    assert sample_task.status is TaskStatus.PLANNED
    assert sample_task.schedule == Schedule()
    assert sample_task.completed_at is None
    assert sample_task.updated_at == restart_at
