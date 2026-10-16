from abc import ABC, abstractmethod
from typing import Generic, TypeVar


TCommand = TypeVar("TCommand")
TResult = TypeVar("TResult")


class Handler(ABC, Generic[TCommand, TResult]):
    """Визначає інтерфейс обробника команди."""

    @abstractmethod
    def execute(self, command: TCommand) -> TResult:
        """Виконує команду та повертає результат."""
        ...
