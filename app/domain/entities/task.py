from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Self

from domain.entities.base import Entity
from domain.enums import ARCHIVED_TASK_STATUSES, TaskPriority, TaskStatus
from domain.exceptions import InvalidTaskException
from domain.value_objects.description import Description
from domain.value_objects.identifiers import TaskId
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title


@dataclass(eq=False, kw_only=True)
class Task(Entity[TaskId]):
    """Завдання користувача з контрольованими переходами стану."""

    title: Title
    description: Description
    status: TaskStatus
    priority: TaskPriority
    schedule: Schedule
    completed_at: Optional[datetime]

    @classmethod
    def create(
        cls, *,
        id: TaskId,
        title: Title,
        now: datetime,
        description: Description,
        priority: TaskPriority = TaskPriority.LOW,
        schedule: Optional[Schedule] = None,

    ) -> Self:
        return cls(
            id=id,
            title=title,
            description=description,
            status=TaskStatus.PLANNED,
            priority=priority,
            schedule=schedule if schedule is not None else Schedule(),
            completed_at=None,
            created_at=now,
            updated_at=now,
        )

    @property
    def is_planned(self):
        return self.status is TaskStatus.PLANNED

    @property
    def is_archived(self):
        return self.status in ARCHIVED_TASK_STATUSES

    def edit(self, title: Title, description: Description,
             priority: TaskPriority, schedule: Schedule, now: datetime):
        if not self.is_planned:
            raise InvalidTaskException("Редагувати можна лише заплановане завдання")

        self.title = title
        self.description = description
        self.priority = priority
        self.schedule = schedule
        self._touch(now)

    def complete(self, now: datetime):
        if not self.is_planned:
            raise InvalidTaskException("Виконати можна лише заплановане завдання")

        self.status = TaskStatus.COMPLETED
        self.completed_at = now
        self._touch(now)

    def mark_not_completed(self, now: datetime):
        if not self.is_planned:
            raise InvalidTaskException("Позначити невиконаним можна лише заплановане завдання")

        self.status = TaskStatus.NOT_COMPLETED
        self.completed_at = None
        self._touch(now)

    def cancel(self, now: datetime):
        if not self.is_planned:
            raise InvalidTaskException("Скасувати можна лише заплановане завдання")

        self.status = TaskStatus.CANCELLED
        self.completed_at = None
        self._touch(now)

    def restart(self, now: datetime):
        if not self.is_archived:
            raise InvalidTaskException("Перезапустити можна лише архівне завдання")

        self.status = TaskStatus.PLANNED
        self.schedule = Schedule()
        self.completed_at = None
        self._touch(now)
