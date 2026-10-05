from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4

from domain.exceptions import ValidationException
from domain.value_objects.base import ValueObject


@dataclass(frozen=True)
class EntityId(ValueObject):
    value: str

    def _validate(self) -> None:
        try:
            UUID(self.value)
        except (ValueError, AttributeError, TypeError):
            raise ValidationException(f"Invalid {type(self).__name__}: {self.value!r}")

    @classmethod
    def new(cls) -> Self:
        return cls(str(uuid4()))

    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class TaskId(EntityId): ...