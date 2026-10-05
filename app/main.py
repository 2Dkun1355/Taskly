from pathlib import Path

from application.mediator import Mediator
from application.use_cases.change_task_status import ChangeTaskStatusCommand, ChangeTaskStatusHandler
from application.use_cases.create_task import CreateTaskCommand, CreateTaskHandler
from application.use_cases.delete_task import DeleteTaskCommand, DeleteTaskHandler
from application.use_cases.list_tasks import ListTasksCommand, ListTasksHandler
from application.use_cases.update_task import UpdateTaskCommand, UpdateTaskHandler
from infrastructure.persistence.json.json_storage import JsonStorage
from infrastructure.persistence.json.json_unit_of_work import JsonUnitOfWork
from presentation.kivy.app import TasklyApp
from presentation.kivy.task_gateway import TaskGateway


def build_mediator() -> Mediator:
    uow = JsonUnitOfWork(JsonStorage(Path("data/taskly.json")))

    mediator = Mediator()
    mediator.register(CreateTaskCommand, CreateTaskHandler(uow))
    mediator.register(UpdateTaskCommand, UpdateTaskHandler(uow))
    mediator.register(DeleteTaskCommand, DeleteTaskHandler(uow))
    mediator.register(ListTasksCommand, ListTasksHandler(uow))
    mediator.register(ChangeTaskStatusCommand, ChangeTaskStatusHandler(uow))
    return mediator


def build_app() -> TasklyApp:
    return TasklyApp(TaskGateway(build_mediator()))

if __name__ == "__main__":
    build_app().run()