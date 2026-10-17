from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Self

from domain.entities.base import Entity
from domain.enums import TaskPriority, TaskStatus
from domain.exceptions import InvalidTaskException, ValidationException
from domain.value_objects.identifiers import TaskId
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title


MAX_DESCRIPTION_LENGTH = 2000

_ARCHIVED_STATUSES = frozenset({
    TaskStatus.COMPLETED,
    TaskStatus.NOT_COMPLETED,
    TaskStatus.CANCELLED,
})


@dataclass(eq=False, kw_only=True)
class Task(Entity[TaskId]):
    """Завдання користувача."""

    title: Title
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    schedule: Schedule
    completed_at: Optional[datetime]

    @classmethod
    def create(
        cls,
        title: Title,
        now: datetime,
        description: Optional[str] = None,
        priority: TaskPriority = TaskPriority.LOW,
        schedule: Optional[Schedule] = None,
    ) -> Self:
        """Створює заплановане завдання."""
        task = cls(
            id=TaskId.new(),
            title=title,
            description=cls._normalize_description(description),
            status=TaskStatus.PLANNED,
            priority=priority,
            schedule=schedule if schedule is not None else Schedule(),
            completed_at=None,
            created_at=now,
            updated_at=now,
        )

        return task

    @property
    def is_planned(self):
        """Перевіряє, чи завдання заплановане."""
        return self.status is TaskStatus.PLANNED

    @property
    def is_archived(self):
        """Перевіряє, чи завдання перебуває в архіві."""
        return self.status in _ARCHIVED_STATUSES

    @property
    def is_in_inbox(self):
        """Перевіряє, чи завдання не має дат."""
        return (
            self.is_planned
            and self.schedule.start_at is None
            and self.schedule.end_at is None
        )

    def edit(
        self,
        title: Title,
        description: Optional[str],
        priority: TaskPriority,
        schedule: Schedule,
        now: datetime,
    ):
        """Редагує заплановане завдання."""
        if not self.is_planned:
            raise InvalidTaskException(
                "Редагувати можна лише заплановане завдання"
            )

        if not isinstance(title, Title):
            raise ValidationException("Назва завдання повинна мати тип Title")

        if not isinstance(priority, TaskPriority):
            raise ValidationException("Некоректний пріоритет завдання")

        if not isinstance(schedule, Schedule):
            raise ValidationException("Некоректний розклад завдання")

        description = self._normalize_description(description)
        self.title = title
        self.description = description
        self.priority = priority
        self.schedule = schedule
        self._touch(now)

    def complete(self, now: datetime):
        """Позначає завдання виконаним."""
        if not self.is_planned:
            raise InvalidTaskException(
                "Виконати можна лише заплановане завдання"
            )

        self.status = TaskStatus.COMPLETED
        self.completed_at = now
        self._touch(now)

    def mark_not_completed(self, now: datetime):
        """Позначає завдання невиконаним."""
        if not self.is_planned:
            raise InvalidTaskException(
                "Позначити невиконаним можна лише заплановане завдання"
            )

        self.status = TaskStatus.NOT_COMPLETED
        self.completed_at = None
        self._touch(now)

    def cancel(self, now: datetime):
        """Скасовує заплановане завдання."""
        if not self.is_planned:
            raise InvalidTaskException(
                "Скасувати можна лише заплановане завдання"
            )

        self.status = TaskStatus.CANCELLED
        self._touch(now)

    def restart(self, now: datetime):
        """Повертає архівне завдання до запланованого стану."""
        if not self.is_archived:
            raise InvalidTaskException(
                "Перезапустити можна лише архівне завдання"
            )

        self.status = TaskStatus.PLANNED
        self.schedule = Schedule()
        self.completed_at = None
        self._touch(now)

    @staticmethod
    def _normalize_description(description: Optional[str]) -> Optional[str]:
        """Перевіряє, очищає та нормалізує необов'язковий опис."""
        if description is None:
            return None
        if not isinstance(description, str):
            raise ValidationException("Опис завдання повинен бути рядком")

        normalized = description.strip()
        if not normalized:
            return None
        if len(normalized) > MAX_DESCRIPTION_LENGTH:
            raise ValidationException(
                "Опис завдання не може бути довшим за "
                f"{MAX_DESCRIPTION_LENGTH} символів"
            )
        return normalized
