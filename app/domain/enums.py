from enum import IntEnum, StrEnum


class TaskPriority(IntEnum):
    """Пріоритет завдання. Числові значення дозволяють порівнювати й сортувати."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class TaskStatus(StrEnum):
    """Статус завдання, який зберігається: що з ним сталося."""

    PLANNED = "planned"
    COMPLETED = "completed"
    NOT_COMPLETED = "not_completed"
    CANCELLED = "cancelled"


ARCHIVED_TASK_STATUSES = frozenset({
    TaskStatus.COMPLETED,
    TaskStatus.NOT_COMPLETED,
    TaskStatus.CANCELLED,
})
