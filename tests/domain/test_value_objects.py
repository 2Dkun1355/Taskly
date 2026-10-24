from datetime import datetime, timedelta, timezone

import pytest

from domain.enums import TaskPriority, TaskStatus
from domain.exceptions import ValidationException
from domain.value_objects.description import MAX_DESCRIPTION_LENGTH, Description
from domain.value_objects.identifiers import EntityId, TaskId
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import MAX_TITLE_LENGTH, Title


def test_title_is_normalized_and_validated():
    assert Title("  Назва  ").value == "Назва"

    with pytest.raises(ValidationException):
        Title(" ")
    with pytest.raises(ValidationException):
        Title("x" * (MAX_TITLE_LENGTH + 1))


def test_description_is_normalized_and_validated():
    assert Description("  опис\n").value == "опис"

    with pytest.raises(ValidationException):
        Description("x" * (MAX_DESCRIPTION_LENGTH + 1))


def test_identifiers_require_uuid():
    identifier = TaskId.new()
    assert TaskId(identifier.value) == identifier
    assert EntityId(identifier.value) != identifier

    with pytest.raises(ValidationException):
        TaskId("not-a-uuid")


def test_schedule_accepts_supported_combinations():
    end = datetime(2026, 1, 15, 13, tzinfo=timezone.utc)
    start = end - timedelta(hours=1)

    assert Schedule() == Schedule(None, None)
    assert Schedule(end_at=end).end_at == end
    assert Schedule(start_at=start, end_at=end).start_at == start


def test_schedule_rejects_start_without_end_and_invalid_interval():
    start = datetime(2026, 1, 15, 12, tzinfo=timezone.utc)

    with pytest.raises(ValidationException):
        Schedule(start_at=start)
    with pytest.raises(ValidationException):
        Schedule(start_at=start, end_at=start)


def test_schedule_rejects_naive_and_non_utc_datetimes():
    naive = datetime(2026, 1, 15, 12)
    kyiv_time = datetime(
        2026,
        1,
        15,
        12,
        tzinfo=timezone(timedelta(hours=2)),
    )

    with pytest.raises(ValidationException, match="UTC"):
        Schedule(end_at=naive)
    with pytest.raises(ValidationException, match="UTC"):
        Schedule(end_at=kyiv_time)


def test_enum_labels_are_available():
    assert TaskPriority.HIGH.label == "високий"
    assert TaskStatus.COMPLETED.label == "виконано"
