from datetime import datetime, timedelta, timezone

import pytest

from domain.entities.task import Task
from domain.enums import TaskPriority, TaskStatus
from domain.value_objects.description import Description
from domain.value_objects.identifiers import TaskId
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title
from application.interfaces import TaskRepository, UnitOfWork


NOW = datetime(2026, 1, 15, 12, tzinfo=timezone.utc)


@pytest.fixture
def task_factory():
    def create(
        number=1,
        *,
        title=None,
        description="опис",
        priority=TaskPriority.LOW,
        schedule=None,
        status=TaskStatus.PLANNED,
        updated_at=None,
    ):
        task = Task.create(
            id=TaskId(f"00000000-0000-0000-0000-{number:012d}"),
            title=Title(title or f"Завдання {number}"),
            now=NOW,
            description=Description(description),
            priority=priority,
            schedule=schedule,
        )
        task.status = status
        task.updated_at = updated_at or NOW
        return task

    return create


@pytest.fixture
def sample_task(task_factory):
    return task_factory()


@pytest.fixture
def unit_of_work():
    return InMemoryUnitOfWork()


@pytest.fixture
def scheduled_task(task_factory):
    return task_factory(
        schedule=Schedule(
            start_at=NOW + timedelta(hours=1),
            end_at=NOW + timedelta(hours=2),
        )
    )


class InMemoryTaskRepository(TaskRepository):
    def __init__(self):
        self._tasks = {}

    def get_by_id(self, task_id):
        return self._tasks.get(task_id.value)

    def get_all(self):
        return list(self._tasks.values())

    def add(self, task):
        if task.id.value in self._tasks:
            raise ValueError("Завдання вже існує")
        self._tasks[task.id.value] = task

    def update(self, task):
        if task.id.value not in self._tasks:
            raise ValueError("Завдання не знайдено")
        self._tasks[task.id.value] = task

    def delete(self, task_id):
        if task_id.value not in self._tasks:
            raise ValueError("Завдання не знайдено")
        del self._tasks[task_id.value]


class InMemoryUnitOfWork(UnitOfWork):
    def __init__(self):
        self._repository = InMemoryTaskRepository()
        self._entered = False

    @property
    def tasks(self):
        return self._repository

    def __enter__(self):
        if self._entered:
            raise RuntimeError("UnitOfWork вже використовується")
        self._entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._entered = False
        return False

    def commit(self):
        if not self._entered:
            raise RuntimeError("UnitOfWork потрібно використовувати через with")

    def rollback(self):
        if not self._entered:
            raise RuntimeError("UnitOfWork потрібно використовувати через with")
