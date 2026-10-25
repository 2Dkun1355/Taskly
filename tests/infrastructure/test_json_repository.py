import pytest

from application.interfaces import TaskSearchCriteria
from domain.enums import TaskStatus
from infrastructure.persistence.json.json_task_repository import JsonTaskRepository


def test_repository_add_get_update_and_delete(sample_task):
    repository = JsonTaskRepository({})
    repository.add(sample_task)

    assert repository.get_by_id(sample_task.id) == sample_task
    criteria = TaskSearchCriteria(statuses=frozenset({TaskStatus.PLANNED}))
    assert repository.search(criteria) == [sample_task]

    sample_task.title = sample_task.title
    repository.update(sample_task)
    repository.delete(sample_task.id)
    assert repository.search(criteria) == []


def test_repository_rejects_duplicate_and_missing_tasks(sample_task, task_factory):
    repository = JsonTaskRepository({})
    repository.add(sample_task)

    with pytest.raises(ValueError):
        repository.add(sample_task)
    with pytest.raises(ValueError):
        repository.update(task_factory(2))
    with pytest.raises(ValueError):
        repository.delete(task_factory(2).id)
