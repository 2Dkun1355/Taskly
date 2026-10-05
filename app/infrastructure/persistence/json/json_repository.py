from abc import abstractmethod
from typing import Iterator, TypeVar

from application.interfaces.repositories.base import Repository
from domain.entities.base import Entity

TEntity = TypeVar("TEntity", bound=Entity)
TId = TypeVar("TId")


class JsonRepository(Repository[TEntity, TId]):
    def __init__(self, items: dict):
        self._items = items

    def add(self, entity: TEntity):
        self._items[str(entity.id)] = self.to_dict(entity)

    def get(self, entity_id: TId) -> TEntity:
        raw = self._items.get(str(entity_id))
        if raw is None:
            raise self._not_found(entity_id)
        return self.from_dict(raw)

    def save(self, entity: TEntity):
        self._ensure_exists(entity.id)
        self._items[str(entity.id)] = self.to_dict(entity)

    def delete(self, entity_id: TId):
        self._ensure_exists(entity_id)
        del self._items[str(entity_id)]

    @abstractmethod
    def _not_found(self, entity_id: TId) -> Exception: ...

    def _ensure_exists(self, entity_id: TId):
        if str(entity_id) not in self._items:
            raise self._not_found(entity_id)

    def _all(self) -> Iterator[TEntity]:
        return (self.from_dict(raw) for raw in self._items.values())