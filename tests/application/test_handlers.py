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