from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from domain.exceptions import ValidationException
from domain.value_objects.base import ValueObject


@dataclass(frozen=True)
class Schedule(ValueObject):
    """Розклад завдання з необов'язковим часом початку та дедлайном."""

    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None

    def __post_init__(self):
        object.__setattr__(self, "start_at", self._to_utc(self.start_at))
        object.__setattr__(self, "end_at", self._to_utc(self.end_at))
        super().__post_init__()

    def _validate(self):
        """Перевіряє правильність часових меж."""
        if (
            self.start_at is not None
            and self.end_at is not None
            and self.start_at >= self.end_at
        ):
            raise ValidationException(
                "Початок розкладу повинен бути раніше за дедлайн"
            )

    @staticmethod
    def _to_utc(value: Optional[datetime]):
        """Перетворює дату в UTC."""
        if value is None:
            return None

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValidationException(
                "Дати розкладу повинні містити часовий пояс"
            )

        return value.astimezone(timezone.utc)
