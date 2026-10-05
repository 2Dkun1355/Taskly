from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "pending"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    COMPLETED = "completed"