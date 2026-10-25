from application.queries import ListTasksQuery, TaskSection
from application.queries.list_tasks import ListTasksHandler
from domain.enums import TaskPriority, TaskStatus


def test_active_query_supports_priority():
    command = ListTasksQuery(
        section=TaskSection.ALL_ACTIVE,
        priority=TaskPriority.HIGH,
    )
    criteria = ListTasksHandler.build_search_criteria(command)

    assert criteria.priority is TaskPriority.HIGH


def test_upcoming_criteria_excludes_inbox():
    command = ListTasksQuery(section=TaskSection.UPCOMING)
    criteria = ListTasksHandler.build_search_criteria(command)

    assert criteria.scheduled_after is not None
    assert criteria.statuses == frozenset({TaskStatus.PLANNED})


def test_archive_filter_is_ignored_for_active_sections(task_factory):
    criteria = ListTasksHandler.build_search_criteria(
        ListTasksQuery(
            section=TaskSection.ALL_ACTIVE,
            status=TaskStatus.COMPLETED,
        )
    )

    assert criteria.statuses == frozenset({TaskStatus.PLANNED})
