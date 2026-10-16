from abc import ABC, abstractmethod

from application.interfaces.task_repository import TaskRepository


class UnitOfWork(ABC):
    """Керує сховищами та транзакціями."""

    @property
    @abstractmethod
    def tasks(self) -> TaskRepository:
        """Повертає сховище завдань."""
        ...

    @abstractmethod
    def commit(self):
        """Підтверджує зміни."""
        ...

    @abstractmethod
    def rollback(self):
        """Скасовує незбережені зміни."""
        ...

    def __enter__(self):
        """Починає роботу з одиницею збереження."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Відкочує транзакцію в разі помилки."""
        if exc_type is not None:
            self.rollback()
