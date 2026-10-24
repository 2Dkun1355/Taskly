from enum import IntEnum, StrEnum


class TaskPriority(IntEnum):
    """Пріоритет завдання. Числові значення дозволяють порівнювати й сортувати."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @property
    def label(self):
        """Назва пріоритету для показу користувачу."""
        return {
            TaskPriority.LOW: "низький",
            TaskPriority.MEDIUM: "середній",
            TaskPriority.HIGH: "високий",
        }[self]


class TaskStatus(StrEnum):
    """Статус завдання, який зберігається: що з ним сталося."""

    PLANNED = "planned"
    COMPLETED = "completed"
    NOT_COMPLETED = "not_completed"
    CANCELLED = "cancelled"

    @property
    def label(self) -> str:
        """Назва статусу для показу користувачу."""
        return {
            TaskStatus.PLANNED: "заплановано",
            TaskStatus.COMPLETED: "виконано",
            TaskStatus.NOT_COMPLETED: "не виконано",
            TaskStatus.CANCELLED: "скасовано",
        }[self]


ARCHIVED_TASK_STATUSES = frozenset({
    TaskStatus.COMPLETED,
    TaskStatus.NOT_COMPLETED,
    TaskStatus.CANCELLED,
})
