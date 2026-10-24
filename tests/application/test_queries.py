from datetime import datetime, timedelta, timezone

from application.queries import ListTasksQuery, TaskSection
from application.queries.list_tasks import TaskListSpecificationFactory
from domain.enums import TaskPriority
from domain.value_objects.schedule import Schedule


def test_active_query_supports_search_and_priority(task_factory):
    command = ListTasksQuery(
        section=TaskSection.ALL,
        search="важлива",
        min_priority="HIGH",
    )
    specification = TaskListSpecificationFactory.create(command)
    matching = task_factory(
        title="Важлива задача",
        priority=TaskPriority.HIGH,
    )
    non_matching = task_factory(2, title="Інша задача")

    assert specification.is_satisfied_by(matching)
    assert not specification.is_satisfied_by(non_matching)


def test_upcoming_specification_excludes_inbox(task_factory):
    command = ListTasksQuery(section=TaskSection.UPCOMING)
    specification = TaskListSpecificationFactory.create(command)

    inbox = task_factory()
    scheduled = task_factory(
        2,
        schedule=Schedule(
            end_at=datetime.now(timezone.utc) + timedelta(days=2)
        ),
    )

    assert not specification.is_satisfied_by(inbox)
    assert specification.is_satisfied_by(scheduled)
