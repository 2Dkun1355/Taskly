from datetime import datetime

from domain.entities.task import Task
from domain.enums import TaskPriority, TaskStatus
from domain.value_objects.identifiers import TaskId
from domain.value_objects.description import Description
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title


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
                task.schedule.start_at.isoformat()
                if task.schedule.start_at
                else None
            ),
            "end_at": (
                task.schedule.end_at.isoformat()
                if task.schedule.end_at
                else None
            ),
        },
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "completed_at": (
            task.completed_at.isoformat()
            if task.completed_at
            else None
        ),
    }


def task_from_dict(data: dict) -> Task:
    """Відновлює доменне завдання зі словника."""
    created_at = datetime.fromisoformat(data["created_at"])
    schedule_data = data["schedule"]

    schedule = Schedule(
        start_at=(
            datetime.fromisoformat(schedule_data["start_at"])
            if schedule_data["start_at"]
            else None
        ),
        end_at=(
            datetime.fromisoformat(schedule_data["end_at"])
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

    task.status = TaskStatus(data["status"])
    task.updated_at = datetime.fromisoformat(data["updated_at"])
    task.completed_at = (
        datetime.fromisoformat(data["completed_at"])
        if data["completed_at"]
        else None
    )

    return task
