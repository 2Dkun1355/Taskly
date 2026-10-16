from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4

from domain.exceptions import ValidationException
from domain.value_objects.base import ValueObject


@dataclass(frozen=True)
class EntityId(ValueObject):
    """Унікальний ідентифікатор сутності на основі UUID."""

    value: str

    def _validate(self):
        try:
            UUID(self.value)
        except (ValueError, AttributeError, TypeError):
            raise ValidationException(
                f"Некоректний ідентифікатор {type(self).__name__}: {self.value!r}"
            ) from None

    @classmethod
    def new(cls) -> Self:
        """Створює новий ідентифікатор."""
        return cls(str(uuid4()))

    def __str__(self):
        """Повертає ідентифікатор у вигляді рядка."""
        return self.value


@dataclass(frozen=True)
class TaskId(EntityId):
    """Ідентифікатор завдання."""
