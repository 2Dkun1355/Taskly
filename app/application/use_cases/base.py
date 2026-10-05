from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TCommand = TypeVar("TCommand")
TResult = TypeVar("TResult")

class Command(Generic[TResult]): ...

class Handler(ABC, Generic[TCommand, TResult]):
    @abstractmethod
    def handle(self, command: TCommand) -> TResult: ...