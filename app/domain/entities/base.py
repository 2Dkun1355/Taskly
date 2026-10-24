from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar


TId = TypeVar("TId")


@dataclass(eq=False, kw_only=True)
class Entity(Generic[TId]):
    """Базова сутність з унікальним ідентифікатором."""

    id: TId
    created_at: datetime
    updated_at: datetime

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.id == other.id
        )

    def __hash__(self):
        return hash((type(self), self.id))

    def _touch(self, now: datetime):
        """Оновлює час останньої зміни."""
        self.updated_at = now
        return now
