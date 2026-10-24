from dataclasses import dataclass
from domain.exceptions import ValidationException
from domain.value_objects.base import ValueObject


MAX_DESCRIPTION_LENGTH = 2000


@dataclass(frozen=True)
class Description(ValueObject):
    """Необов'язковий нормалізований опис завдання."""

    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise ValidationException("Опис завдання повинен бути рядком")

        object.__setattr__(self, "value", self.value.strip())
        super().__post_init__()

    def _validate(self):
        if len(self.value) > MAX_DESCRIPTION_LENGTH:
            raise ValidationException(
                "Опис завдання не може бути довшим за "
                f"{MAX_DESCRIPTION_LENGTH} символів"
            )

    def __str__(self):
        return self.value
