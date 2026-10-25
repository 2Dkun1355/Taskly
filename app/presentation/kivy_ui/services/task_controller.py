from domain.enums import TaskPriority, TaskStatus

from application.queries.list_tasks import TaskSection
from presentation.kivy_ui.services.task_service import TaskService


class TaskController:
    """Керує станом списку та взаємодією UI із TaskService."""

    def __init__(self, service: TaskService):
        self.service = service
        self.section = TaskSection.ALL_ACTIVE
        self.search = ""
        self.priority: TaskPriority | None = None
        self.archive_status: TaskStatus | None = None
        self.pending_priority: TaskPriority | None = None
        self.pending_archive_status: TaskStatus | None = None
        self.loaded_tasks = ()

    def refresh(self):
        is_archive = self.section is TaskSection.ARCHIVE
        result = self.service.select(
            self.section,
            self.archive_status if is_archive else None,
            priority=self.priority,
        )
        self.loaded_tasks = result.tasks
        return result.tasks

    def visible_tasks(self):
        search = self.search.strip().casefold()
        return tuple(
            task for task in self.loaded_tasks
            if not search or search in task.title.value.casefold()
        )

    def select_section(self, section):
        self.section = section

    def set_search(self, value):
        self.search = value

    def begin_filter_edit(self):
        self.pending_priority = self.priority
        self.pending_archive_status = self.archive_status

    def set_pending_priority(self, value):
        self.pending_priority = TaskPriority[value] if value != "all" else None

    def set_pending_archive_status(self, value):
        self.pending_archive_status = TaskStatus(value) if value != "all" else None

    def apply_filters(self):
        self.priority = self.pending_priority
        self.archive_status = self.pending_archive_status

    def reset_filters(self):
        self.priority = None
        self.archive_status = None
