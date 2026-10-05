from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Self

from domain.entities.base import Entity
from domain.enums.task_priority import TaskPriority
from domain.enums.task_status import TaskStatus
from domain.exceptions import InvalidTaskException
from domain.value_objects.identifiers import TaskId
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title

_RESTARTABLE_STATUSES = frozenset({TaskStatus.COMPLETED, TaskStatus.CANCELLED})


@dataclass(eq=False)
class Task(Entity[TaskId]):
    title: Title
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    schedule: Schedule
    completed_at: Optional[datetime]

    @classmethod
    def create(cls, title: Title, description: Optional[str] = None,
               priority: TaskPriority = TaskPriority.MEDIUM,
               schedule: Optional[Schedule] = None) -> Self:
        now = cls._now()
        return cls(
            id=TaskId.new(),
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=priority,
            schedule=schedule or Schedule.empty(),
            completed_at=None,
            created_at=now,
            updated_at=now,
        )

    @property
    def is_pending(self) -> bool:
        return self.status is TaskStatus.PENDING

    def is_overdue(self, now: datetime) -> bool:
        return self.is_pending and self.schedule.has_ended(now)

    def edit(self, title: Title, description: Optional[str], priority: TaskPriority):
        self._ensure_pending("edited")
        self.title = title
        self.description = description
        self.priority = priority
        self._touch()

    def reschedule(self, schedule: Schedule):
        self._ensure_pending("rescheduled")
        self.schedule = schedule
        self._touch()

    def complete(self):
        self._ensure_pending("completed")
        self.status = TaskStatus.COMPLETED
        self.completed_at = self._touch()

    def cancel(self):
        self._ensure_pending("cancelled")
        self.status = TaskStatus.CANCELLED
        self._touch()

    def restart(self, schedule: Optional[Schedule] = None):
        if self.status not in _RESTARTABLE_STATUSES:
            raise InvalidTaskException(
                f"Task cannot be restarted from status '{self.status}'"
            )

        self.status = TaskStatus.PENDING
        self.completed_at = None
        self.schedule = schedule or Schedule.empty()
        self._touch()

    def _ensure_pending(self, action: str):
        if not self.is_pending:
            raise InvalidTaskException(
                f"Task cannot be {action} from status '{self.status}'"
            )