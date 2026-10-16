from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from domain.events import (
    DomainEvent,
    TaskCancelled,
    TaskCompleted,
    TaskCreated,
    TaskNotCompleted,
    TaskRestarted,
)
from domain.value_objects.identifiers import TaskId


def test_domain_event_stores_occurrence_time():
    moment = datetime(2026, 5, 1, 12, tzinfo=timezone.utc)
    event = DomainEvent(occurred_at=moment)

    assert event.occurred_at == moment


@pytest.mark.parametrize(
    "event_type",
    [
        TaskCreated,
        TaskCompleted,
        TaskNotCompleted,
        TaskCancelled,
        TaskRestarted,
    ],
)
def test_task_event_stores_task_id_and_time(event_type):
    moment = datetime(2026, 5, 1, 12, tzinfo=timezone.utc)
    task_id = TaskId.new()

    event = event_type(occurred_at=moment, task_id=task_id)

    assert event.occurred_at == moment
    assert event.task_id == task_id


def test_domain_events_are_immutable():
    event = TaskCreated(
        occurred_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
        task_id=TaskId.new(),
    )

    with pytest.raises(FrozenInstanceError):
        event.task_id = TaskId.new()