from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.task import Task
from domain.value_objects.identifiers import TaskId


class TaskRepository(ABC):
    """Визначає операції для роботи із завданнями."""

    @abstractmethod
    def get_by_id(self, task_id: TaskId) -> Optional[Task]:
        """Знаходить завдання за ідентифікатором."""
        ...

    @abstractmethod
    def get_all(self) -> list[Task]:
        """Повертає всі завдання."""
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
