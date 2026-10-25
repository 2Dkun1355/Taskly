from datetime import datetime, timezone

import pytest

from domain.enums import TaskPriority, TaskStatus
from domain.exceptions import ValidationException
from domain.value_objects.schedule import Schedule
from infrastructure.persistence.json.task_mapper import task_from_dict, task_to_dict


def test_task_mapper_round_trip_preserves_task(sample_task):
    restored = task_from_dict(task_to_dict(sample_task))

    assert restored == sample_task
    assert restored.description == sample_task.description
    assert restored.schedule == sample_task.schedule


def test_task_mapper_preserves_optional_schedule_and_completed_at(task_factory):
    completed_at = datetime(2026, 1, 15, 13, tzinfo=timezone.utc)
    task = task_factory(
        status=TaskStatus.COMPLETED,
        priority=TaskPriority.HIGH,
        schedule=Schedule(end_at=completed_at),
    )
    task.completed_at = completed_at

    restored = task_from_dict(task_to_dict(task))

    assert restored.status is TaskStatus.COMPLETED
    assert restored.priority is TaskPriority.HIGH
    assert restored.completed_at == completed_at
    assert restored.schedule.end_at == completed_at


def test_task_mapper_rejects_naive_metadata(sample_task):
    data = task_to_dict(sample_task)
    data["created_at"] = "2026-01-15T12:00:00"

    with pytest.raises(ValidationException, match="часову зону"):
        task_from_dict(data)


def test_task_mapper_rejects_inconsistent_completion_state(sample_task):
    data = task_to_dict(sample_task)
    data["status"] = TaskStatus.COMPLETED.value

    with pytest.raises(ValidationException, match="completed_at"):
        task_from_dict(data)
