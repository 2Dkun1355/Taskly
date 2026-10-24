from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from domain.exceptions import ValidationException
from domain.value_objects.base import ValueObject


@dataclass(frozen=True)
class Schedule(ValueObject):
    """Розклад завдання з необов'язковим часом початку та дедлайном."""

    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None

    def __post_init__(self):
        super().__post_init__()

    def _validate(self):
        """Перевіряє правильність часових меж."""
        for value in (self.start_at, self.end_at):
            if value is not None and (
                value.tzinfo is None
                or value.utcoffset() is None
                or value.utcoffset() != timedelta(0)
            ):
                raise ValidationException(
                    "Час розкладу повинен бути в часовій зоні UTC"
                )

        if self.start_at is not None and self.end_at is None:
            raise ValidationException(
                "Початок розкладу повинен мати кінцевий час"
            )

        if (
            self.start_at is not None
            and self.end_at is not None
            and self.start_at >= self.end_at
        ):
            raise ValidationException(
                "Початок розкладу повинен бути раніше за дедлайн"
            )
