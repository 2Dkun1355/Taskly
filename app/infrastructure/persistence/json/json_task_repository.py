from domain.entities.task import Task
from domain.value_objects.identifiers import TaskId

from application.interfaces.task_repository import TaskRepository


class JsonTaskRepository(TaskRepository):
    """Зберігає завдання в пам'яті протягом транзакції."""

    def __init__(self, tasks: dict[str, Task]):
        self._tasks = tasks

    def get_by_id(self, task_id: TaskId) -> Task | None:
        """Знаходить завдання за ідентифікатором."""
        return self._tasks.get(task_id.value)

    def get_all(self) -> list[Task]:
        """Повертає всі завдання."""
        return list(self._tasks.values())

    def add(self, task: Task):
        """Додає нове завдання."""
        task_id = task.id.value

        if task_id in self._tasks:
            raise ValueError(f"Завдання {task_id} вже існує")

        self._tasks[task_id] = task

    def update(self, task: Task):
        """Оновлює наявне завдання."""
        task_id = task.id.value

        if task_id not in self._tasks:
            raise ValueError(f"Завдання {task_id} не знайдено")

        self._tasks[task_id] = task

    def delete(self, task_id: TaskId):
        """Видаляє завдання за ідентифікатором."""
        if task_id.value not in self._tasks:
            raise ValueError(f"Завдання {task_id.value} не знайдено")

        del self._tasks[task_id.value]
