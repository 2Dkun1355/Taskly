from application.commands.cancel_task import CancelTaskCommand
from application.commands.clear_archive import ClearArchiveCommand
from application.commands.complete_task import CompleteTaskCommand
from application.commands.create_task import CreateTaskCommand
from application.commands.delete_task import DeleteTaskCommand
from application.commands.edit_task import EditTaskCommand
from application.commands.mark_task_not_completed import MarkTaskNotCompletedCommand
from application.commands.restart_task import RestartTaskCommand
from application.queries.list_tasks import ListTasksQuery


class TaskService:
    def __init__(self, mediator):
        self._mediator = mediator

    def select(self, section, status=None, priority=None):
        return self._mediator.send(ListTasksQuery(
            section=section,
            status=status,
            priority=priority,
        ))

    def create_task(self, title, description, priority, start_at, end_at):
        return self._mediator.send(CreateTaskCommand(
            title=title, description=description, priority=priority,
            start_at=start_at, end_at=end_at,
        ))

    def edit_task(self, task, title, description, priority, start_at, end_at):
        return self._mediator.send(EditTaskCommand(
            task_id=task.id, title=title, description=description,
            priority=priority, start_at=start_at, end_at=end_at,
        ))

    def complete(self, task):
        return self._mediator.send(CompleteTaskCommand(task_id=task.id))

    def mark_not_completed(self, task):
        return self._mediator.send(MarkTaskNotCompletedCommand(task_id=task.id))

    def cancel(self, task):
        return self._mediator.send(CancelTaskCommand(task_id=task.id))

    def restart(self, task):
        return self._mediator.send(RestartTaskCommand(task_id=task.id))

    def delete(self, task):
        return self._mediator.send(DeleteTaskCommand(task_id=task.id))

    def clear_archive(self):
        result = self._mediator.send(ClearArchiveCommand())
        return result.deleted_count
