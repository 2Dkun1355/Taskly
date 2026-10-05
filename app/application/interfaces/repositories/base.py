from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from domain.entities.base import Entity

TEntity = TypeVar("TEntity", bound=Entity)
TId = TypeVar("TId")


class Repository(ABC, Generic[TEntity, TId]):
    @abstractmethod
    def add(self, entity: TEntity): ...

    @abstractmethod
    def get(self, entity_id: TId) -> TEntity: ...

    @abstractmethod
    def save(self, entity: TEntity): ...

    @abstractmethod
    def delete(self, entity_id: TId): ...

    @abstractmethod
    def to_dict(self, entity: TEntity) -> dict: ...

    @abstractmethod
    def from_dict(self, data: dict) -> TEntity: ...