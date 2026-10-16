from copy import deepcopy
from datetime import datetime, timezone

import pytest

from domain.entities.task import Task
from domain.enums import TaskPriority
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title


class InMemoryTaskRepository:
    """Тестове сховище завдань у пам'яті."""

    def __init__(self, tasks):
        self._tasks = tasks

    def get_by_id(self, task_id):
        return self._tasks.get(task_id.value)

    def get_all(self):
        return list(self._tasks.values())

    def add(self, task):
        key = task.id.value
        if key in self._tasks:
            raise ValueError(f"Завдання {key} вже існує")
        self._tasks[key] = task

    def update(self, task):
        key = task.id.value
        if key not in self._tasks:
            raise ValueError(f"Завдання {key} не знайдено")
        self._tasks[key] = task

    def delete(self, task_id):
        if task_id.value not in self._tasks:
            raise ValueError(f"Завдання {task_id.value} не знайдено")
        del self._tasks[task_id.value]


class InMemoryUnitOfWork:
    """Тестова одиниця збереження з підтримкою commit і rollback."""

    def __init__(self, initial_tasks=None):
        self._tasks = {
            task.id.value: task for task in (initial_tasks or [])
        }
        self._repository = InMemoryTaskRepository(self._tasks)
        self._snapshot = None
        self._entered = False
        self.commit_count = 0
        self.rollback_count = 0

    @property
    def tasks(self):
        return self._repository

    def __enter__(self):
        if self._entered:
            raise RuntimeError("UnitOfWork вже використовується")
        self._snapshot = deepcopy(self._tasks)
        self._entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is not None:
                self.rollback()
        finally:
            self._entered = False
            self._snapshot = None
        return False

    def commit(self):
        if not self._entered:
            raise RuntimeError("UnitOfWork не активний")
        self.commit_count += 1
        self._snapshot = deepcopy(self._tasks)

    def rollback(self):
        if not self._entered:
            raise RuntimeError("UnitOfWork не активний")
        self._tasks.clear()
        self._tasks.update(deepcopy(self._snapshot or {}))
        self.rollback_count += 1


@pytest.fixture
def unit_of_work():
    return InMemoryUnitOfWork()


@pytest.fixture
def sample_task():
    return Task.create(
        title=Title("Тестове завдання"),
        now=datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc),
        description="Опис завдання",
        priority=TaskPriority.LOW,
        schedule=Schedule(),
    )


@pytest.fixture
def unit_of_work_with_task(sample_task):
    return InMemoryUnitOfWork([sample_task])
''',
"tests/application/test_mediator.py": r'''"""Тести медіатора."""

from dataclasses import dataclass

import pytest

from application.common import Handler, Mediator


@dataclass(frozen=True)
class ExampleCommand:
    value: str


@dataclass(frozen=True)
class AnotherCommand:
    value: str


class ExampleHandler(Handler[ExampleCommand, str]):
    """Тестовий обробник."""

    def execute(self, command):
        return command.value.upper()


def test_send_returns_handler_result():
    mediator = Mediator()
    mediator.register(ExampleCommand, ExampleHandler())

    assert mediator.send(ExampleCommand("hello")) == "HELLO"


def test_send_passes_original_command_to_handler():
    class RecordingHandler(Handler[ExampleCommand, ExampleCommand]):
        def __init__(self):
            self.received = None

        def execute(self, command):
            self.received = command
            return command

    handler = RecordingHandler()
    mediator = Mediator()
    command = ExampleCommand("value")
    mediator.register(ExampleCommand, handler)

    assert mediator.send(command) is command
    assert handler.received is command


def test_register_rejects_duplicate_type():
    mediator = Mediator()
    mediator.register(ExampleCommand, ExampleHandler())

    with pytest.raises(ValueError):
        mediator.register(ExampleCommand, ExampleHandler())


def test_send_rejects_unregistered_type():
    mediator = Mediator()

    with pytest.raises(LookupError):
        mediator.send(ExampleCommand("hello"))


def test_send_uses_exact_type_not_parent_or_similar_type():
    mediator = Mediator()
    mediator.register(ExampleCommand, ExampleHandler())

    with pytest.raises(LookupError):
        mediator.send(AnotherCommand("hello"))
''',
"tests/application/test_handlers.py": r'''"""Тести обробників команд і запитів."""

from datetime import datetime, timezone

import pytest

from application.commands import (
    CancelTaskCommand,
    CancelTaskHandler,
    CompleteTaskCommand,
    CompleteTaskHandler,
    CreateTaskCommand,
    CreateTaskHandler,
    EditTaskCommand,
    EditTaskHandler,
    MarkTaskNotCompletedCommand,
    MarkTaskNotCompletedHandler,
    RestartTaskCommand,
    RestartTaskHandler,
)
from application.queries import (
    GetTaskHandler,
    GetTaskQuery,
    ListTasksHandler,
    ListTasksQuery,
)
from domain.enums import TaskPriority, TaskStatus
from domain.exceptions import InvalidTaskException
from domain.value_objects.identifiers import TaskId
from domain.value_objects.schedule import Schedule


def create_task(unit_of_work, title="Завдання"):
    result = CreateTaskHandler(unit_of_work).execute(
        CreateTaskCommand(title=title)
    )
    return result.task_id


def test_create_task_persists_task_and_returns_id(unit_of_work):
    result = CreateTaskHandler(unit_of_work).execute(
        CreateTaskCommand(title="Нове завдання")
    )

    task = unit_of_work.tasks.get_by_id(result.task_id)
    assert task is not None
    assert task.title.value == "Нове завдання"
    assert task.status is TaskStatus.PLANNED
    assert task.priority is TaskPriority.LOW
    assert unit_of_work.commit_count == 1


def test_create_task_preserves_optional_fields(unit_of_work):
    result = CreateTaskHandler(unit_of_work).execute(
        CreateTaskCommand(
            title="Завдання з описом",
            description="Детальний опис",
            priority=TaskPriority.LOW,
            schedule=Schedule(),
        )
    )

    task = unit_of_work.tasks.get_by_id(result.task_id)
    assert task.description == "Детальний опис"
    assert task.schedule == Schedule()


def test_get_task_returns_requested_task(unit_of_work_with_task, sample_task):
    result = GetTaskHandler(unit_of_work_with_task).execute(
        GetTaskQuery(task_id=sample_task.id)
    )

    assert result.task.id == sample_task.id
    assert result.task.title.value == sample_task.title.value


def test_get_task_raises_for_missing_id(unit_of_work):
    with pytest.raises(InvalidTaskException):
        GetTaskHandler(unit_of_work).execute(
            GetTaskQuery(task_id=TaskId.new())
        )


def test_list_tasks_returns_all_tasks(unit_of_work_with_task, sample_task):
    result = ListTasksHandler(unit_of_work_with_task).execute(ListTasksQuery())

    assert len(result.tasks) == 1
    assert result.tasks[0].id == sample_task.id


def test_list_tasks_returns_empty_tuple_when_empty(unit_of_work):
    result = ListTasksHandler(unit_of_work).execute(ListTasksQuery())

    assert result.tasks == ()


def test_edit_task_updates_fields(unit_of_work):
    task_id = create_task(unit_of_work)
    result = EditTaskHandler(unit_of_work).execute(
        EditTaskCommand(
            task_id=task_id,
            title="Оновлена назва",
            description="Оновлений опис",
            priority=TaskPriority.LOW,
            schedule=Schedule(),
        )
    )

    task = unit_of_work.tasks.get_by_id(task_id)
    assert result.task_id == task_id
    assert task.title.value == "Оновлена назва"
    assert task.description == "Оновлений опис"
    assert unit_of_work.commit_count == 2


def test_edit_task_raises_for_missing_id(unit_of_work):
    with pytest.raises(InvalidTaskException):
        EditTaskHandler(unit_of_work).execute(
            EditTaskCommand(
                task_id=TaskId.new(),
                title="Назва",
                description=None,
                priority=TaskPriority.LOW,
                schedule=Schedule(),
            )
        )


def test_complete_task_changes_status(unit_of_work):
    task_id = create_task(unit_of_work)

    CompleteTaskHandler(unit_of_work).execute(CompleteTaskCommand(task_id))

    task = unit_of_work.tasks.get_by_id(task_id)
    assert task.status is TaskStatus.COMPLETED
    assert task.completed_at is not None


def test_complete_task_raises_for_missing_id(unit_of_work):
    with pytest.raises(InvalidTaskException):
        CompleteTaskHandler(unit_of_work).execute(
            CompleteTaskCommand(TaskId.new())
        )


def test_cancel_task_changes_status(unit_of_work):
    task_id = create_task(unit_of_work)

    CancelTaskHandler(unit_of_work).execute(CancelTaskCommand(task_id))

    assert unit_of_work.tasks.get_by_id(task_id).status is TaskStatus.CANCELLED


def test_cancel_completed_task_is_rejected(unit_of_work):
    task_id = create_task(unit_of_work)
    CompleteTaskHandler(unit_of_work).execute(CompleteTaskCommand(task_id))
    commits_before = unit_of_work.commit_count

    with pytest.raises(InvalidTaskException):
        CancelTaskHandler(unit_of_work).execute(CancelTaskCommand(task_id))

    assert unit_of_work.tasks.get_by_id(task_id).status is TaskStatus.COMPLETED
    assert unit_of_work.commit_count == commits_before


def test_cancel_task_raises_for_missing_id(unit_of_work):
    with pytest.raises(InvalidTaskException):
        CancelTaskHandler(unit_of_work).execute(
            CancelTaskCommand(TaskId.new())
        )


def test_mark_not_completed_changes_status(unit_of_work):
    task_id = create_task(unit_of_work)

    MarkTaskNotCompletedHandler(unit_of_work).execute(
        MarkTaskNotCompletedCommand(task_id)
    )

    assert (
        unit_of_work.tasks.get_by_id(task_id).status
        is TaskStatus.NOT_COMPLETED
    )


def test_mark_not_completed_raises_for_missing_id(unit_of_work):
    with pytest.raises(InvalidTaskException):
        MarkTaskNotCompletedHandler(unit_of_work).execute(
            MarkTaskNotCompletedCommand(TaskId.new())
        )


@pytest.mark.parametrize(
    "initial_status",
    [TaskStatus.COMPLETED, TaskStatus.CANCELLED, TaskStatus.NOT_COMPLETED],
)
def test_restart_archived_task_clears_schedule_and_completion(
    unit_of_work, initial_status
):
    task_id = create_task(unit_of_work)
    task = unit_of_work.tasks.get_by_id(task_id)
    task.status = initial_status
    if initial_status is TaskStatus.COMPLETED:
        task.completed_at = datetime.now(timezone.utc)
    task.schedule = Schedule()

    RestartTaskHandler(unit_of_work).execute(RestartTaskCommand(task_id))

    restarted = unit_of_work.tasks.get_by_id(task_id)
    assert restarted.status is TaskStatus.PLANNED
    assert restarted.completed_at is None
    assert restarted.schedule == Schedule()


def test_restart_planned_task_raises(unit_of_work):
    task_id = create_task(unit_of_work)

    with pytest.raises(InvalidTaskException):
        RestartTaskHandler(unit_of_work).execute(RestartTaskCommand(task_id))


def test_restart_task_raises_for_missing_id(unit_of_work):
    with pytest.raises(InvalidTaskException):
        RestartTaskHandler(unit_of_work).execute(
            RestartTaskCommand(TaskId.new())
        )
''',
"tests/infrastructure/test_json_storage.py": r'''"""Тести JSONStorage."""

import json

import pytest

from infrastructure.persistence.json.json_storage import JsonStorage


def test_load_returns_empty_list_when_file_missing(tmp_path):
    storage = JsonStorage(tmp_path / "missing.json")

    assert storage.load() == []


def test_save_creates_parent_directory_and_file(tmp_path):
    path = tmp_path / "nested" / "data.json"
    storage = JsonStorage(path)

    storage.save([{"title": "Завдання"}])

    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8")) == [
        {"title": "Завдання"}
    ]


def test_save_and_load_preserve_unicode(tmp_path):
    storage = JsonStorage(tmp_path / "tasks.json")
    data = [{"title": "Український текст", "description": "їжак, ґанок"}]

    storage.save(data)

    assert storage.load() == data
    assert "Український текст" in storage._file_path.read_text(encoding="utf-8")


def test_load_rejects_non_list_json(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text('{"task": "value"}', encoding="utf-8")

    with pytest.raises(ValueError):
        JsonStorage(path).load()


def test_load_propagates_invalid_json(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text("[broken", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        JsonStorage(path).load()


def test_save_replaces_existing_content(tmp_path):
    storage = JsonStorage(tmp_path / "tasks.json")
    storage.save([{"id": "old"}])
    storage.save([{"id": "new"}])

    assert storage.load() == [{"id": "new"}]


def test_save_leaves_no_temporary_file_after_success(tmp_path):
    path = tmp_path / "tasks.json"
    JsonStorage(path).save([])

    assert not path.with_suffix(".json.tmp").exists()