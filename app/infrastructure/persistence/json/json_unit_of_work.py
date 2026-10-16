from application.interfaces.unit_of_work import UnitOfWork
from domain.entities.task import Task

from infrastructure.persistence.json.json_storage import JsonStorage
from infrastructure.persistence.json.json_task_repository import JsonTaskRepository
from infrastructure.persistence.json.task_mapper import task_from_dict, task_to_dict


class JsonUnitOfWork(UnitOfWork):
    """Керує змінами завдань у межах робочого контексту."""

    def __init__(self, storage: JsonStorage | None = None):
        self._storage = storage or JsonStorage()
        self._tasks: dict[str, Task] = {}
        self._repository = JsonTaskRepository(self._tasks)
        self._entered = False

    @property
    def tasks(self) -> JsonTaskRepository:
        """Повертає репозиторій завдань."""
        return self._repository

    def __enter__(self):
        """Завантажує завдання перед початком роботи."""
        if self._entered:
            raise RuntimeError("UnitOfWork вже використовується")

        self._load()
        self._entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Відкочує незбережені зміни в разі помилки."""
        try:
            if exc_type is not None:
                self.rollback()
        finally:
            self._entered = False

        return False

    def commit(self):
        """Зберігає зміни."""
        self._ensure_entered()

        data = [
            task_to_dict(task)
            for task in self._tasks.values()
        ]
        self._storage.save(data)

    def rollback(self):
        """Відновлює стан із JSON-файлу."""
        self._ensure_entered()
        self._load()

    def _load(self):
        """Завантажує та відновлює доменні об'єкти."""
        loaded_tasks = [
            task_from_dict(item)
            for item in self._storage.load()
        ]

        tasks = {}

        for task in loaded_tasks:
            task_id = task.id.value

            if task_id in tasks:
                raise ValueError(f"Дубльований ID завдання: {task_id}")

            tasks[task_id] = task

        self._tasks.clear()
        self._tasks.update(tasks)

    def _ensure_entered(self):
        """Перевіряє активність робочого контексту."""
        if not self._entered:
            raise RuntimeError("UnitOfWork потрібно використовувати через with")
