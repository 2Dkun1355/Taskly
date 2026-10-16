from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """Базовий клас для незмінних об'єктів-значень.

    Рівність визначається значеннями полів. Перевірка інваріантів
    виконується автоматично одразу після створення об'єкта.
    """

    def __post_init__(self):
        self._validate()

    def _validate(self):
        """Перевіряє інваріанти. Нащадки перевизначають і кидають ValidationException."""