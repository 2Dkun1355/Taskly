from dataclasses import dataclass

import pytest

from application.common import Handler, Mediator


@dataclass(frozen=True)
class ExampleMessage:
    value: str


class ExampleHandler(Handler[ExampleMessage, str]):
    def execute(self, command):
        return command.value.upper()


def test_mediator_sends_message_to_registered_handler():
    mediator = Mediator()
    mediator.register(ExampleMessage, ExampleHandler())

    assert mediator.send(ExampleMessage("ok")) == "OK"


def test_mediator_rejects_duplicate_or_unknown_handlers():
    mediator = Mediator()
    mediator.register(ExampleMessage, ExampleHandler())

    with pytest.raises(ValueError):
        mediator.register(ExampleMessage, ExampleHandler())
    with pytest.raises(LookupError):
        mediator.send("unknown")
