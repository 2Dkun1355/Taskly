from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Self

from domain.exceptions import ValidationException
from domain.value_objects.base import ValueObject


@dataclass(frozen=True)
class Schedule(ValueObject):
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None

    def __post_init__(self):
        object.__setattr__(self, "start_at", self._to_utc(self.start_at))
        object.__setattr__(self, "end_at", self._to_utc(self.end_at))
        super().__post_init__()

    @classmethod
    def empty(cls) -> Self:
        return cls()

    @classmethod
    def deadline(cls, end_at: datetime) -> Self:
        return cls(end_at=end_at)

    @classmethod
    def interval(cls, start_at: datetime, end_at: datetime) -> Self:
        return cls(start_at=start_at, end_at=end_at)

    @property
    def is_empty(self) -> bool:
        return self.start_at is None and self.end_at is None

    @property
    def is_interval(self) -> bool:
        return self.start_at is not None and self.end_at is not None

    def has_ended(self, now: datetime) -> bool:
        return self.end_at is not None and now > self.end_at

    def overlaps(self, other: Self) -> bool:
        if not (self.is_interval and other.is_interval):
            return False
        return self.start_at < other.end_at and other.start_at < self.end_at

    def _validate(self):
        if self.start_at is not None and self.end_at is None:
            raise ValidationException("Schedule with a start must also have an end")
        if self.is_interval and self.start_at >= self.end_at:
            raise ValidationException("Schedule start must be before its end")

    @staticmethod
    def _to_utc(value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValidationException("Schedule datetimes must be timezone-aware")
        return value.astimezone(timezone.utc)