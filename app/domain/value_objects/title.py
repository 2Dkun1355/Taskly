from dataclasses import dataclass

from domain.exceptions import ValidationException
from domain.value_objects.base import ValueObject


MAX_TITLE_LENGTH = 128


@dataclass(frozen=True)
class Title(ValueObject):
    """Назва завдання."""

    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise ValidationException("Назва завдання повинна бути рядком")

        object.__setattr__(self, "value", self.value.strip())
        super().__post_init__()

    def _validate(self):
        """Перевіряє назву завдання."""
        if not self.value:
            raise ValidationException("Назва завдання не може бути порожньою")

        if len(self.value) > MAX_TITLE_LENGTH:
            raise ValidationException(
                f"Назва завдання не може бути довшою за {MAX_TITLE_LENGTH} символів"
            )

    def __str__(self):
        """Повертає назву у вигляді рядка."""
        return self.value