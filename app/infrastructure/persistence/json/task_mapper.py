from datetime import datetime

from domain.entities.task import Task
from domain.enums import TaskPriority, TaskStatus
from domain.exceptions import ValidationException
from domain.value_objects.identifiers import TaskId
from domain.value_objects.description import Description
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title


def _parse_aware_datetime(value: str, field_name: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValidationException(
            f"Поле {field_name} повинно містити часову зону"
        )
    return parsed.astimezone()


def _local_isoformat(value: datetime) -> str:
    return value.astimezone().isoformat()


def task_to_dict(task: Task) -> dict:
    """Перетворює завдання на словник для JSON."""
    return {
        "id": task.id.value,
        "title": task.title.value,
        "description": task.description.value,
        "status": task.status.value,
        "priority": task.priority.value,
        "schedule": {
            "start_at": (
                _local_isoformat(task.schedule.start_at)
                if task.schedule.start_at
                else None
            ),
            "end_at": (
                _local_isoformat(task.schedule.end_at)
                if task.schedule.end_at
                else None
            ),
        },
        "created_at": _local_isoformat(task.created_at),
        "updated_at": _local_isoformat(task.updated_at),
        "completed_at": (
            _local_isoformat(task.completed_at)
            if task.completed_at
            else None
        ),
    }


def task_from_dict(data: dict) -> Task:
    """Відновлює доменне завдання зі словника."""
    created_at = _parse_aware_datetime(data["created_at"], "created_at")
    schedule_data = data["schedule"]

    schedule = Schedule(
        start_at=(
            _parse_aware_datetime(schedule_data["start_at"], "start_at")
            if schedule_data["start_at"]
            else None
        ),
        end_at=(
            _parse_aware_datetime(schedule_data["end_at"], "end_at")
            if schedule_data["end_at"]
            else None
        ),
    )

    task = Task.create(
        id=TaskId(data["id"]),
        title=Title(data["title"]),
        now=created_at,
        description=Description(data["description"] or ""),
        priority=TaskPriority(data["priority"]),
        schedule=schedule,
    )

    status = TaskStatus(data["status"])
    updated_at = _parse_aware_datetime(data["updated_at"], "updated_at")
    completed_at = (
        _parse_aware_datetime(data["completed_at"], "completed_at")
        if data["completed_at"]
        else None
    )

    if (status is TaskStatus.COMPLETED) != (completed_at is not None):
        raise ValidationException(
            "Виконане завдання повинно мати completed_at, "
            "а невиконане — не повинно його мати"
        )

    task.status = status
    task.updated_at = updated_at
    task.completed_at = completed_at

    return task
