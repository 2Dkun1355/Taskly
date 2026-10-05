from abc import abstractmethod

from application.interfaces.repositories.base import Repository
from domain.entities.task import Task
from domain.value_objects.identifiers import TaskId


class TaskRepository(Repository[Task, TaskId]):
    @abstractmethod
    def list_all(self) -> list[Task]: ...