import json

import pytest

from infrastructure.persistence.json.json_storage import JsonStorage
from infrastructure.persistence.json.json_unit_of_work import JsonUnitOfWork


def test_unit_of_work_loads_and_commits_tasks(tmp_path, sample_task):
    storage = JsonStorage(tmp_path / "tasks.json")

    with JsonUnitOfWork(storage) as unit_of_work:
        unit_of_work.tasks.add(sample_task)
        unit_of_work.commit()

    with JsonUnitOfWork(storage) as unit_of_work:
        assert unit_of_work.tasks.get_by_id(sample_task.id) == sample_task


def test_unit_of_work_rolls_back_failed_transaction(tmp_path, sample_task):
    storage = JsonStorage(tmp_path / "tasks.json")

    with pytest.raises(RuntimeError):
        with JsonUnitOfWork(storage) as unit_of_work:
            unit_of_work.tasks.add(sample_task)
            raise RuntimeError("failure")

    assert storage.load() == []


def test_unit_of_work_rejects_duplicate_ids_in_file(tmp_path, sample_task):
    storage = JsonStorage(tmp_path / "tasks.json")
    data = {
        "id": sample_task.id.value,
        "title": sample_task.title.value,
        "description": sample_task.description.value,
        "status": sample_task.status.value,
        "priority": sample_task.priority.value,
        "schedule": {"start_at": None, "end_at": None},
        "created_at": sample_task.created_at.isoformat(),
        "updated_at": sample_task.updated_at.isoformat(),
        "completed_at": None,
    }
    storage.save([data, data])

    with pytest.raises(ValueError, match="Дубльований ID"):
        with JsonUnitOfWork(storage):
            pass
