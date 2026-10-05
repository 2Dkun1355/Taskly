from abc import ABC, abstractmethod
from typing import Self

from application.interfaces.repositories.task_repository import TaskRepository


class UnitOfWork(ABC):
    tasks: TaskRepository

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type is not None:
            self.rollback()

    @abstractmethod
    def commit(self): ...

    @abstractmethod
    def rollback(self): ...