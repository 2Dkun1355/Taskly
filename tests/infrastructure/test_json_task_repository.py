import pytest

from infrastructure.persistence.json.json_task_repository import JsonTaskRepository


def test_add_and_get_by_id(sample_task):
    tasks = {}
    repository = JsonTaskRepository(tasks)

    repository.add(sample_task)

    assert repository.get_by_id(sample_task.id) is sample_task


def test_add_rejects_duplicate_id(sample_task):
    repository = JsonTaskRepository({sample_task.id.value: sample_task})

    with pytest.raises(ValueError):
        repository.add(sample_task)


def test_get_by_id_returns_none_for_missing_id(sample_task):
    repository = JsonTaskRepository({})

    assert repository.get_by_id(sample_task.id) is None


def test_get_all_returns_all_tasks(sample_task):
    repository = JsonTaskRepository({sample_task.id.value: sample_task})

    assert repository.get_all() == [sample_task]


def test_update_replaces_existing_task(sample_task):
    repository = JsonTaskRepository({sample_task.id.value: sample_task})
    sample_task.description = "Оновлено"

    repository.update(sample_task)

    assert repository.get_by_id(sample_task.id).description == "Оновлено"


def test_update_rejects_missing_task(sample_task):
    repository = JsonTaskRepository({})

    with pytest.raises(ValueError):
        repository.update(sample_task)


def test_delete_removes_task(sample_task):
    repository = JsonTaskRepository({sample_task.id.value: sample_task})

    repository.delete(sample_task.id)

    assert repository.get_all() == []


def test_delete_rejects_missing_task(sample_task):
    repository = JsonTaskRepository({})

    with pytest.raises(ValueError):
        repository.delete(sample_task.id)