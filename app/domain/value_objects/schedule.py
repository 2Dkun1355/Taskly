from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.exceptions import ValidationException
from domain.value_objects.base import ValueObject


@dataclass(frozen=True)
class Schedule(ValueObject):
    """Розклад завдання з необов'язковим часом початку та дедлайном."""

    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None

    def _validate(self):
        """Перевіряє правильність часових меж."""
        for value in (self.start_at, self.end_at):
            if value is not None and (
                value.tzinfo is None
                or value.utcoffset() is None
            ):
                raise ValidationException(
                    "Час розкладу повинен містити часову зону"
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
