from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generic, TypeVar

TId = TypeVar("TId")


@dataclass(eq=False)
class Entity(Generic[TId]):
    id: TId
    created_at: datetime
    updated_at: datetime

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if type(self) is not type(other):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def _touch(self) -> datetime:
        self.updated_at = self._now()
        return self.updated_at