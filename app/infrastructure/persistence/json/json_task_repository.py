from datetime import datetime, time, timedelta

from domain.entities.task import Task
from domain.enums import ARCHIVED_TASK_STATUSES
from domain.value_objects.identifiers import TaskId

from application.interfaces.task_repository import TaskRepository, TaskSearchCriteria


class JsonTaskRepository(TaskRepository):
    """Зберігає завдання в пам'яті протягом транзакції."""

    def __init__(self, tasks: dict[str, Task]):
        self._tasks = tasks

    def get_by_id(self, task_id: TaskId) -> Task | None:
        """Знаходить завдання за ідентифікатором."""
        return self._tasks.get(task_id.value)


    def search(self, criteria: TaskSearchCriteria) -> list[Task]:
        """Шукає завдання відповідно до абстрактних критеріїв."""
        return [
            task for task in self._tasks.values()
            if task.status in criteria.statuses
            and (
                criteria.priority is None
                or task.priority is criteria.priority
            )
            and (
                criteria.scheduled_on is None
                or self._scheduled_on(task, criteria.scheduled_on)
            )
            and (
                criteria.scheduled_after is None
                or self._scheduled_after(task, criteria.scheduled_after)
            )
        ]

    def delete_archived(self) -> int:
        """Видаляє архівні завдання з поточної транзакції."""
        archived_ids = [
            task_id
            for task_id, task in self._tasks.items()
            if task.status in ARCHIVED_TASK_STATUSES
        ]
        for task_id in archived_ids:
            del self._tasks[task_id]
        return len(archived_ids)

    @staticmethod
    def _scheduled_on(task: Task, day) -> bool:
        tzinfo = datetime.now().astimezone().tzinfo
        start = datetime.combine(day, time.min, tzinfo=tzinfo)
        end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=tzinfo)
        task_start = task.schedule.start_at
        task_end = task.schedule.end_at

        if task_start is not None and task_end is not None:
            return task_start < end and task_end > start
        return task_end is not None and start <= task_end < end

    @staticmethod
    def _scheduled_after(task: Task, day) -> bool:
        return any(
            value is not None and value.date() > day
            for value in (task.schedule.start_at, task.schedule.end_at)
        )

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
