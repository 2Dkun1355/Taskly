from datetime import datetime, timezone

from application.mediator import Mediator
from application.use_cases.change_task_status import ChangeTaskStatusCommand
from application.use_cases.create_task import CreateTaskCommand
from application.use_cases.delete_task import DeleteTaskCommand
from application.use_cases.list_tasks import ListTasksCommand
from application.use_cases.update_task import UpdateTaskCommand
from domain.enums.task_status import TaskStatus
from presentation.kivy.filter_bar import TaskFilter
from presentation.kivy.task_view import TaskData, TaskView


class TaskGateway:
    def __init__(self, mediator: Mediator):
        self._mediator = mediator

    def list(self, task_filter: TaskFilter) -> list[TaskView]:
        result = self._mediator.send(ListTasksCommand(
            now=datetime.now(timezone.utc),
            status=task_filter.status,
            only_overdue=task_filter.only_overdue,
        ))
        return [
            TaskView(
                id=item.id,
                title=item.title,
                description=item.description,
                status=item.status,
                priority=item.priority,
                start_at=item.start_at,
                end_at=item.end_at,
                is_overdue=item.is_overdue,
            )
            for item in result.tasks
        ]

    def create(self, data: TaskData):
        self._mediator.send(CreateTaskCommand(
            title=data.title,
            description=data.description,
            priority=data.priority,
            start_at=data.start_at,
            end_at=data.end_at,
        ))

    def update(self, task_id: str, data: TaskData):
        self._mediator.send(UpdateTaskCommand(
            task_id=task_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            start_at=data.start_at,
            end_at=data.end_at,
        ))

    def delete(self, task_id: str):
        self._mediator.send(DeleteTaskCommand(task_id=task_id))

    def change_status(self, task_id: str, status: TaskStatus):
        self._mediator.send(ChangeTaskStatusCommand(task_id=task_id, status=status))