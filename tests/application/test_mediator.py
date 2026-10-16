from dataclasses import dataclass

import pytest

from application.common import Handler, Mediator


@dataclass(frozen=True)
class TestCommand:
    value: str


class TestHandler(Handler[TestCommand, str]):
    """Тестовий обробник."""

    def execute(self, command: TestCommand) -> str:
        """Повертає значення команди."""
        return command.value.upper()


def test_send_executes_registered_handler():
    mediator = Mediator()
    mediator.register(TestCommand, TestHandler())

    result = mediator.send(TestCommand("hello"))

    assert result == "HELLO"


def test_register_rejects_duplicate_handler():
    mediator = Mediator()
    mediator.register(TestCommand, TestHandler())

    with pytest.raises(ValueError, match="вже зареєстрований"):
        mediator.register(TestCommand, TestHandler())


def test_send_rejects_unregistered_command():
    mediator = Mediator()

    with pytest.raises(LookupError, match="не зареєстрований"):
        mediator.send(TestCommand("hello"))


def test_send_uses_exact_command_type():
    @dataclass(frozen=True)
    class AnotherCommand(TestCommand):
        pass

    mediator = Mediator()
    mediator.register(TestCommand, TestHandler())

    with pytest.raises(LookupError):
        mediator.send(AnotherCommand("hello"))
