from datetime import datetime, timedelta
from types import SimpleNamespace

from application.commands import (
    CancelTaskCommand,
    CompleteTaskCommand,
    CreateTaskCommand,
    DeleteTaskCommand,
    EditTaskCommand,
    MarkTaskNotCompletedCommand,
    RestartTaskCommand,
)
from application.queries import ListTasksQuery
from domain.entities.task import Task
from domain.enums import TaskPriority, TaskStatus
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title
from presentation.kivy_ui.services.task_service import (
    SECTION_ALL,
    SECTION_ARCHIVE,
    SECTION_INBOX,
    SECTION_OVERDUE,
    SECTION_TODAY,
    SECTION_UPCOMING,
    TaskService,
)


class SpyMediator:
    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)
        if isinstance(message, ListTasksQuery):
            return SimpleNamespace(tasks=("first", "second"))
        return "result"


def make_task(title, schedule=None, priority=TaskPriority.LOW):
    return Task.create(
        title=Title(title),
        now=datetime.now().astimezone(),
        schedule=schedule,
        priority=priority,
    )


def test_load_tasks_returns_a_list_from_query_result():
    mediator = SpyMediator()

    assert TaskService(mediator).load_tasks() == ["first", "second"]
    assert isinstance(mediator.messages[0], ListTasksQuery)


def test_select_filters_sections_and_searches_by_title():
    now = datetime.now().astimezone()
    tasks = [
        make_task("Сьогодні", Schedule(end_at=now + timedelta(hours=1))),
        make_task("Завтра", Schedule(end_at=now + timedelta(days=2))),
        make_task("Без дати"),
        make_task("Прострочене", Schedule(end_at=now - timedelta(hours=1))),
    ]

    service = TaskService(SpyMediator())

    assert service.select(tasks, SECTION_TODAY, "сьогодні") == [tasks[0]]
    assert service.select(tasks, SECTION_INBOX) == [tasks[2]]
    assert service.select(tasks, SECTION_OVERDUE) == [tasks[3]]
    assert service.select(tasks, SECTION_UPCOMING) == [tasks[1]]


def test_select_sorts_active_tasks_by_due_date_then_priority():
    now = datetime.now().astimezone()
    later = make_task(
        "Пізніше",
        Schedule(end_at=now + timedelta(days=2)),
        TaskPriority.HIGH,
    )
    sooner = make_task(
        "Раніше",
        Schedule(end_at=now + timedelta(days=1)),
        TaskPriority.LOW,
    )
    no_date = make_task("Без дати", priority=TaskPriority.HIGH)

    assert TaskService(SpyMediator()).select(
        [no_date, later, sooner], SECTION_ALL
    ) == [sooner, later, no_date]


def test_select_filters_and_sorts_archive_by_update_time():
    now = datetime.now().astimezone()
    older = make_task("Старе")
    newer = make_task("Нове")
    older.complete(now - timedelta(hours=2))
    newer.complete(now - timedelta(hours=1))

    service = TaskService(SpyMediator())

    assert service.select(
        [older, newer], SECTION_ARCHIVE, archive_status="completed"
    ) == [newer, older]
    assert service.select(
        [older, newer], SECTION_ARCHIVE, archive_status="cancelled"
    ) == []


def test_count_counts_only_tasks_in_requested_section():
    now = datetime.now().astimezone()
    tasks = [
        make_task("Активне"),
        make_task("Виконане"),
    ]
    tasks[1].complete(now)

    assert TaskService(SpyMediator()).count(tasks, SECTION_ALL) == 1
    assert TaskService(SpyMediator()).count(tasks, SECTION_ARCHIVE) == 1


def test_state_of_returns_display_state():
    now = datetime.now().astimezone()
    inbox = make_task("Inbox")
    overdue = make_task("Overdue", Schedule(end_at=now - timedelta(hours=1)))
    planned = make_task("Planned", Schedule(end_at=now + timedelta(hours=1)))
    completed = make_task("Completed")
    completed.complete(now)

    assert TaskService.state_of(inbox) == "inbox"
    assert TaskService.state_of(overdue) == "overdue"
    assert TaskService.state_of(planned) == "planned"
    assert TaskService.state_of(completed) == "completed"


def test_task_actions_send_expected_commands():
    mediator = SpyMediator()
    service = TaskService(mediator)
    task = make_task("Завдання")
    start = datetime.now().astimezone()
    end = start + timedelta(hours=1)

    service.create_task("Нове", " опис ", "HIGH", start, end)
    service.edit_task(task, "Оновлене", "", "MEDIUM", start, end)
    service.complete(task)
    service.mark_not_completed(task)
    service.cancel(task)
    service.restart(task)
    service.delete(task)

    messages = mediator.messages
    assert isinstance(messages[0], CreateTaskCommand)
    assert messages[0].priority is TaskPriority.HIGH
    assert messages[0].description == " опис "
    assert isinstance(messages[1], EditTaskCommand)
    assert messages[1].description is None
    assert isinstance(messages[2], CompleteTaskCommand)
    assert isinstance(messages[3], MarkTaskNotCompletedCommand)
    assert isinstance(messages[4], CancelTaskCommand)
    assert isinstance(messages[5], RestartTaskCommand)
    assert isinstance(messages[6], DeleteTaskCommand)
    assert messages[6].task_id == task.id
