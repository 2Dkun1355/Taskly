from typing import Any

from application.use_cases.base import Command, Handler, TResult


class HandlerNotRegisteredError(LookupError): ...


class Mediator:
    def __init__(self):
        self._handlers: dict[type, Handler] = {}

    def register(self, command_type: type[Command[TResult]], handler: Handler[Any, TResult]):
        if command_type in self._handlers:
            raise ValueError(f"Handler for {command_type.__name__} is already registered")
        self._handlers[command_type] = handler

    def send(self, command: Command[TResult]) -> TResult:
        handler = self._handlers.get(type(command))
        if handler is None:
            raise HandlerNotRegisteredError(
                f"No handler registered for {type(command).__name__}"
            )
        return handler.handle(command)