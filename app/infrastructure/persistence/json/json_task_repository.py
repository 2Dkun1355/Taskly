from datetime import datetime
from typing import Optional

from application.interfaces.repositories.task_repository import TaskRepository
from domain.entities.task import Task
from domain.enums.task_priority import TaskPriority
from domain.enums.task_status import TaskStatus
from domain.exceptions import TaskNotFoundException
from domain.value_objects.identifiers import TaskId
from domain.value_objects.schedule import Schedule
from domain.value_objects.title import Title
from infrastructure.persistence.json.json_repository import JsonRepository


class JsonTaskRepository(JsonRepository[Task, TaskId], TaskRepository):
    def list_all(self) -> list[Task]:
        return list(self._all())

    def to_dict(self, entity: Task) -> dict:
        return {
            "id": str(entity.id),
            "title": str(entity.title),
            "description": entity.description,
            "status": entity.status.value,
            "priority": entity.priority.value,
            "start_at": self._dump(entity.schedule.start_at),
            "end_at": self._dump(entity.schedule.end_at),
            "completed_at": self._dump(entity.completed_at),
            "created_at": self._dump(entity.created_at),
            "updated_at": self._dump(entity.updated_at),
        }

    def from_dict(self, data: dict) -> Task:
        return Task(
            id=TaskId(data["id"]),
            title=Title(data["title"]),
            description=data["description"],
            status=TaskStatus(data["status"]),
            priority=TaskPriority(data["priority"]),
            schedule=Schedule(
                start_at=self._load(data["start_at"]),
                end_at=self._load(data["end_at"]),
            ),
            completed_at=self._load(data["completed_at"]),
            created_at=self._load(data["created_at"]),
            updated_at=self._load(data["updated_at"]),
        )

    def _not_found(self, entity_id: TaskId) -> Exception:
        return TaskNotFoundException(f"Task '{entity_id}' not found")

    @staticmethod
    def _dump(value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None

    @staticmethod
    def _load(value: Optional[str]) -> Optional[datetime]:
        return datetime.fromisoformat(value) if value else None