from datetime import datetime, timedelta, timezone

import pytest

from domain.entities.base import Entity
from domain.enums import TaskPriority, TaskStatus
from domain.exceptions import ValidationException
from domain.value_objects.identifiers import EntityId, TaskId
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import MAX_TITLE_LENGTH, Title


def test_title_strips_whitespace():
    assert Title("  Купити молоко  ").value == "Купити молоко"


@pytest.mark.parametrize("value", ["", "   ", "\n\t"])
def test_title_rejects_empty_value(value):
    with pytest.raises(ValidationException):
        Title(value)


def test_title_rejects_non_string():
    with pytest.raises(ValidationException):
        Title(123)


def test_title_rejects_too_long_value():
    with pytest.raises(ValidationException):
        Title("a" * (MAX_TITLE_LENGTH + 1))


def test_title_accepts_maximum_length():
    assert len(Title("a" * MAX_TITLE_LENGTH).value) == MAX_TITLE_LENGTH


def test_title_string_representation():
    assert str(Title("Завдання")) == "Завдання"


def test_enum_labels_are_localized():
    assert TaskPriority.HIGH.label == "високий"
    assert TaskStatus.COMPLETED.label == "виконано"


def test_entities_compare_by_type_and_id():
    created = datetime(2026, 5, 1, 10, tzinfo=timezone.utc)
    first = Entity(id="same", created_at=created, updated_at=created)
    second = Entity(
        id="same",
        created_at=created + timedelta(days=1),
        updated_at=created,
    )

    assert first == second
    assert hash(first) == hash(second)


def test_entity_id_generates_valid_uuid():
    identifier = EntityId.new()
    assert str(identifier) == identifier.value


def test_task_id_generates_unique_ids():
    first = TaskId.new()
    second = TaskId.new()

    assert first != second
    assert first.value != second.value


def test_entity_id_rejects_invalid_uuid():
    with pytest.raises(ValidationException):
        EntityId("not-a-uuid")


def test_schedule_accepts_no_dates():
    schedule = Schedule()
    assert schedule.start_at is None
    assert schedule.end_at is None


def test_schedule_accepts_start_only():
    start = datetime(2026, 5, 1, 10, tzinfo=timezone.utc)
    schedule = Schedule(start_at=start)

    assert schedule.start_at == start
    assert schedule.end_at is None


def test_schedule_accepts_deadline_only():
    deadline = datetime(2026, 5, 1, 17, tzinfo=timezone.utc)
    schedule = Schedule(end_at=deadline)

    assert schedule.start_at is None
    assert schedule.end_at == deadline


def test_schedule_accepts_valid_interval():
    start = datetime(2026, 5, 1, 10, tzinfo=timezone.utc)
    end = datetime(2026, 5, 1, 11, tzinfo=timezone.utc)

    schedule = Schedule(start_at=start, end_at=end)

    assert schedule.start_at == start
    assert schedule.end_at == end


def test_schedule_rejects_start_equal_to_deadline():
    moment = datetime(2026, 5, 1, 10, tzinfo=timezone.utc)

    with pytest.raises(ValidationException):
        Schedule(start_at=moment, end_at=moment)


def test_schedule_rejects_start_after_deadline():
    start = datetime(2026, 5, 1, 11, tzinfo=timezone.utc)
    end = datetime(2026, 5, 1, 10, tzinfo=timezone.utc)

    with pytest.raises(ValidationException):
        Schedule(start_at=start, end_at=end)


def test_schedule_rejects_naive_datetime():
    with pytest.raises(ValidationException):
        Schedule(start_at=datetime(2026, 5, 1, 10))


def test_schedule_converts_dates_to_utc():
    local_time = timezone(timedelta(hours=3))
    start = datetime(2026, 5, 1, 13, tzinfo=local_time)

    schedule = Schedule(start_at=start)

    assert schedule.start_at == datetime(2026, 5, 1, 10, tzinfo=timezone.utc)
    assert schedule.start_at.utcoffset() == timedelta(0)
