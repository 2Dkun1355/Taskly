from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    def __post_init__(self):
        self._validate()

    def _validate(self): ...