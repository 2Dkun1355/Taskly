from datetime import timedelta

import pytest

from application.bootstrap import create_mediator
from application.commands import (
    CancelTaskCommand,
    CompleteTaskCommand,
    CreateTaskCommand,
    DeleteTaskCommand,
    EditTaskCommand,
    MarkTaskNotCompletedCommand,
    RestartTaskCommand,
)
from application.queries import (
    ArchiveFilter,
    GetTaskQuery,
    ListTasksQuery,
    TaskSection,
)
from domain.enums import TaskPriority, TaskStatus
from domain.exceptions import InvalidTaskException
from domain.value_objects.schedule import Schedule


def test_create_and_get_task_through_mediator(unit_of_work):
    mediator = create_mediator(unit_of_work)
    created = mediator.send(
        CreateTaskCommand(
            title="Нова задача",
            description="Опис",
            priority="HIGH",
        )
    )

    result = mediator.send(GetTaskQuery(created.task_id))
    assert result.task.title.value == "Нова задача"
    assert result.task.description.value == "Опис"
    assert result.task.priority is TaskPriority.HIGH


def test_edit_and_delete_task(unit_of_work):
    mediator = create_mediator(unit_of_work)
    created = mediator.send(CreateTaskCommand(title="Стара назва"))

    mediator.send(
        EditTaskCommand(
            task_id=created.task_id,
            title="Нова назва",
            description="Новий опис",
            priority="MEDIUM",
            start_at=None,
            end_at=None,
        )
    )
    assert mediator.send(GetTaskQuery(created.task_id)).task.title.value == "Нова назва"

    mediator.send(DeleteTaskCommand(created.task_id))
    with pytest.raises(InvalidTaskException):
        mediator.send(GetTaskQuery(created.task_id))


@pytest.mark.parametrize(
    ("command_type", "expected_status"),
    [
        (CompleteTaskCommand, TaskStatus.COMPLETED),
        (MarkTaskNotCompletedCommand, TaskStatus.NOT_COMPLETED),
        (CancelTaskCommand, TaskStatus.CANCELLED),
    ],
)
def test_planned_task_can_be_archived(
    unit_of_work, command_type, expected_status
):
    mediator = create_mediator(unit_of_work)
    created = mediator.send(CreateTaskCommand(title="Задача"))

    mediator.send(command_type(created.task_id))

    assert mediator.send(GetTaskQuery(created.task_id)).task.status is expected_status


def test_restart_returns_archived_task_to_planned_without_schedule(unit_of_work):
    mediator = create_mediator(unit_of_work)
    created = mediator.send(CreateTaskCommand(title="Задача"))
    mediator.send(CompleteTaskCommand(created.task_id))

    mediator.send(RestartTaskCommand(created.task_id))
    task = mediator.send(GetTaskQuery(created.task_id)).task

    assert task.status is TaskStatus.PLANNED
    assert task.schedule == Schedule()


def test_list_tasks_applies_sections_filters_and_archive_sorting(
    unit_of_work, task_factory
):
    tasks = [
        task_factory(
            1,
            title="Сьогодні",
            schedule=Schedule(
                end_at=task_factory(10).created_at + timedelta(hours=1)
            ),
        ),
        task_factory(2, title="Inbox"),
        task_factory(3, title="Архів", status=TaskStatus.COMPLETED),
    ]
    with unit_of_work as uow:
        for task in tasks:
            uow.tasks.add(task)
        uow.commit()

    from application.queries.list_tasks import ListTasksHandler

    handler = ListTasksHandler(unit_of_work)
    assert [task.title.value for task in handler.execute(
        ListTasksQuery(section=TaskSection.INBOX)
    ).tasks] == ["Inbox"]
    assert [task.title.value for task in handler.execute(
        ListTasksQuery(
            section=TaskSection.ARCHIVE,
            archive_filter=ArchiveFilter.COMPLETED,
        )
    ).tasks] == ["Архів"]
