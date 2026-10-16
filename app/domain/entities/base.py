from dataclasses import dataclass, field
from datetime import datetime
from typing import Generic, TypeVar


TId = TypeVar("TId")


@dataclass(eq=False, kw_only=True)
class Entity(Generic[TId]):
    """Базова сутність.

    Дві сутності рівні, якщо збігаються їхній тип та ідентифікатор,
    незалежно від значень інших полів. Час передається ззовні (через
    параметр now), тому сутність не залежить від системного годинника.
    """

    id: TId
    created_at: datetime
    updated_at: datetime

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __hash__(self):
        return hash((type(self), self.id))

    def _touch(self, now: datetime):
        """Оновлює час останньої зміни й повертає його."""
        self.updated_at = now
        return now
