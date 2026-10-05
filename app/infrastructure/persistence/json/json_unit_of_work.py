from typing import Self

from application.interfaces.unit_of_work import UnitOfWork
from infrastructure.persistence.json.json_storage import JsonStorage
from infrastructure.persistence.json.json_task_repository import JsonTaskRepository


class JsonUnitOfWork(UnitOfWork):
    def __init__(self, storage: JsonStorage):
        self._storage = storage
        self._data: dict = {}

    def __enter__(self) -> Self:
        self._load()
        return self

    def commit(self):
        self._storage.save(self._data)

    def rollback(self):
        self._load()

    def _load(self):
        self._data = self._storage.load()
        self.tasks = JsonTaskRepository(self._data["tasks"])