from abc import ABC, abstractmethod

from domain.entities.task import Task


class Specification(ABC):
    """Умова відбору завдань із підтримкою логічних операторів."""

    @abstractmethod
    def is_satisfied_by(self, task: Task) -> bool:
        """Перевіряє, чи відповідає завдання умові."""
        ...

    def __and__(self, other: "Specification"):
        """Об'єднує умови через логічне І."""
        return _And(self, other)

    def __or__(self, other: "Specification"):
        """Об'єднує умови через логічне АБО."""
        return _Or(self, other)

    def __invert__(self):
        """Інвертує умову."""
        return _Not(self)


class _And(Specification):
    """Перевіряє виконання обох умов."""

    def __init__(self, left: Specification, right: Specification):
        self._left = left
        self._right = right

    def is_satisfied_by(self, task: Task) -> bool:
        """Перевіряє обидві умови."""
        return (
            self._left.is_satisfied_by(task)
            and self._right.is_satisfied_by(task)
        )


class _Or(Specification):
    """Перевіряє виконання хоча б однієї умови."""

    def __init__(self, left: Specification, right: Specification):
        self._left = left
        self._right = right

    def is_satisfied_by(self, task: Task) -> bool:
        """Перевіряє хоча б одну умову."""
        return (
            self._left.is_satisfied_by(task)
            or self._right.is_satisfied_by(task)
        )


class _Not(Specification):
    """Інвертує результат іншої умови."""

    def __init__(self, inner: Specification):
        self._inner = inner

    def is_satisfied_by(self, task: Task) -> bool:
        """Повертає протилежний результат умови."""
        return not self._inner.is_satisfied_by(task)
