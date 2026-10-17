from application.common import Mediator
from application.commands import (
    CancelTaskCommand,
    CancelTaskHandler,
    CompleteTaskCommand,
    CompleteTaskHandler,
    CreateTaskCommand,
    CreateTaskHandler,
    EditTaskCommand,
    EditTaskHandler,
    MarkTaskNotCompletedCommand,
    MarkTaskNotCompletedHandler,
    RestartTaskCommand,
    RestartTaskHandler,
    DeleteTaskCommand,
    DeleteTaskHandler,
)
from application.interfaces import UnitOfWork
from application.queries import (
    GetTaskHandler,
    GetTaskQuery,
    ListTasksHandler,
    ListTasksQuery,
)


def create_mediator(unit_of_work: UnitOfWork) -> Mediator:
    """Створює медіатор із зареєстрованими обробниками."""
    mediator = Mediator()

    handlers = {
        CreateTaskCommand: CreateTaskHandler(unit_of_work),
        EditTaskCommand: EditTaskHandler(unit_of_work),
        DeleteTaskCommand: DeleteTaskHandler(unit_of_work),
        CompleteTaskCommand: CompleteTaskHandler(unit_of_work),
        CancelTaskCommand: CancelTaskHandler(unit_of_work),
        RestartTaskCommand: RestartTaskHandler(unit_of_work),
        MarkTaskNotCompletedCommand: MarkTaskNotCompletedHandler(unit_of_work),
        GetTaskQuery: GetTaskHandler(unit_of_work),
        ListTasksQuery: ListTasksHandler(unit_of_work),
    }

    for message_type, handler in handlers.items():
        mediator.register(message_type, handler)

    return mediator
