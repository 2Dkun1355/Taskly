from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Optional

from domain.entities.task import Task
from domain.enums import TaskPriority, TaskStatus
from domain.value_objects.identifiers import TaskId


@dataclass(frozen=True)
class TaskSearchCriteria:
    """Параметри пошуку без прив'язки до конкретного сховища."""

    statuses: frozenset[TaskStatus]
    priority: Optional[TaskPriority] = None
    scheduled_on: Optional[date] = None
    scheduled_after: Optional[date] = None


class TaskRepository(ABC):
    """Визначає операції для роботи із завданнями."""

    @abstractmethod
    def get_by_id(self, task_id: TaskId) -> Optional[Task]:
        """Знаходить завдання за ідентифікатором."""
        ...

    @abstractmethod
    def search(self, criteria: TaskSearchCriteria) -> list[Task]:
        """Повертає завдання відповідно до критеріїв пошуку."""
        ...

    @abstractmethod
    def add(self, task: Task):
        """Додає завдання до сховища."""
        ...

    @abstractmethod
    def update(self, task: Task):
        """Оновлює завдання у сховищі."""
        ...

    @abstractmethod
    def delete(self, task_id: TaskId):
        """Видаляє завдання зі сховища."""
        ...

    @abstractmethod
    def delete_archived(self) -> int:
        """Видаляє архівні завдання та повертає їх кількість."""
        ...
