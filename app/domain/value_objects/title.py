from dataclasses import dataclass

from domain.exceptions import ValidationException
from domain.value_objects.base import ValueObject


@dataclass(frozen=True)
class Title(ValueObject):
    value: str

    def __post_init__(self):
        object.__setattr__(self, "value", self.value.strip())
        super().__post_init__()

    def _validate(self):
        if not self.value:
            raise ValidationException("Title must not be empty")

    def __str__(self) -> str:
        return self.value