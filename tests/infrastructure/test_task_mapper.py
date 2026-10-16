from datetime import datetime, timezone

from domain.enums import TaskPriority, TaskStatus
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title
from domain.entities.task import Task
from infrastructure.persistence.json.task_mapper import task_from_dict, task_to_dict


def test_task_mapper_round_trip_preserves_fields(sample_task):
    restored = task_from_dict(task_to_dict(sample_task))

    assert restored.id == sample_task.id
    assert restored.title.value == sample_task.title.value
    assert restored.description == sample_task.description
    assert restored.status is sample_task.status
    assert restored.priority == sample_task.priority
    assert restored.schedule == sample_task.schedule
    assert restored.completed_at == sample_task.completed_at


def test_mapper_preserves_unicode(sample_task):
    sample_task.title = Title("Завдання українською")
    sample_task.description = "Перевірка ґ, ї, є, і"

    restored = task_from_dict(task_to_dict(sample_task))

    assert restored.title.value == "Завдання українською"
    assert restored.description == "Перевірка ґ, ї, є, і"


def test_mapper_preserves_completed_task(sample_task):
    sample_task.status = TaskStatus.COMPLETED
    sample_task.completed_at = datetime(2026, 1, 11, 10, 30, tzinfo=timezone.utc)

    restored = task_from_dict(task_to_dict(sample_task))

    assert restored.status is TaskStatus.COMPLETED
    assert restored.completed_at == sample_task.completed_at


def test_mapper_preserves_optional_schedule_values(sample_task):
    sample_task.schedule = Schedule()

    restored = task_from_dict(task_to_dict(sample_task))

    assert restored.schedule == sample_task.schedule
''',
"tests/infrastructure/test_json_unit_of_work.py": r'''"""Тести JSONUnitOfWork."""

import json

import pytest

from infrastructure.persistence.json.json_storage import JsonStorage
from infrastructure.persistence.json.json_unit_of_work import JsonUnitOfWork
from infrastructure.persistence.json.task_mapper import task_to_dict


def test_enter_loads_existing_tasks(tmp_path, sample_task):
    path = tmp_path / "tasks.json"
    path.write_text(
        json.dumps([task_to_dict(sample_task)]),
        encoding="utf-8",
    )
    uow = JsonUnitOfWork(JsonStorage(path))

    with uow:
        loaded = uow.tasks.get_by_id(sample_task.id)
        assert loaded is not None
        assert loaded.title.value == sample_task.title.value


def test_commit_persists_added_task(tmp_path, sample_task):
    path = tmp_path / "tasks.json"
    uow = JsonUnitOfWork(JsonStorage(path))

    with uow:
        uow.tasks.add(sample_task)
        uow.commit()

    assert path.exists()
    assert len(json.loads(path.read_text(encoding="utf-8"))) == 1


def test_committed_task_is_available_in_new_uow(tmp_path, sample_task):
    storage = JsonStorage(tmp_path / "tasks.json")
    first = JsonUnitOfWork(storage)

    with first:
        first.tasks.add(sample_task)
        first.commit()

    second = JsonUnitOfWork(storage)
    with second:
        assert second.tasks.get_by_id(sample_task.id) is not None


def test_rollback_discards_uncommitted_addition(tmp_path, sample_task):
    storage = JsonStorage(tmp_path / "tasks.json")
    uow = JsonUnitOfWork(storage)

    with uow:
        uow.tasks.add(sample_task)
        uow.rollback()
        assert uow.tasks.get_by_id(sample_task.id) is None


def test_context_rolls_back_after_exception(tmp_path, sample_task):
    storage = JsonStorage(tmp_path / "tasks.json")
    uow = JsonUnitOfWork(storage)

    with pytest.raises(RuntimeError):
        with uow:
            uow.tasks.add(sample_task)
            raise RuntimeError("test error")

    with JsonUnitOfWork(storage) as fresh_uow:
        assert fresh_uow.tasks.get_by_id(sample_task.id) is None


def test_commit_requires_active_context(tmp_path):
    uow = JsonUnitOfWork(JsonStorage(tmp_path / "tasks.json"))

    with pytest.raises(RuntimeError):
        uow.commit()


def test_nested_context_is_rejected(tmp_path):
    uow = JsonUnitOfWork(JsonStorage(tmp_path / "tasks.json"))

    with uow:
        with pytest.raises(RuntimeError):
            uow.__enter__()


def test_duplicate_ids_in_file_are_rejected(tmp_path, sample_task):
    path = tmp_path / "tasks.json"
    payload = task_to_dict(sample_task)
    path.write_text(json.dumps([payload, payload]), encoding="utf-8")
    uow = JsonUnitOfWork(JsonStorage(path))

    with pytest.raises(ValueError, match="Дубльований ID"):
        uow.__enter__()