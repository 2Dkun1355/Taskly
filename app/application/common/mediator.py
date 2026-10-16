from typing import Any


class Mediator:
    """Передає повідомлення відповідним обробникам."""

    def __init__(self):
        self._handlers = {}

    def register(self, message_type: type, handler: Any):
        """Реєструє обробник для типу повідомлення."""
        if message_type in self._handlers:
            raise ValueError(
                f"Обробник для {message_type.__name__} вже зареєстрований"
            )

        self._handlers[message_type] = handler

    def send(self, message: Any):
        """Передає повідомлення відповідному обробнику."""
        message_type = type(message)
        handler = self._handlers.get(message_type)

        if handler is None:
            raise LookupError(
                f"Обробник для {message_type.__name__} не зареєстрований"
            )

        return handler.execute(message)
