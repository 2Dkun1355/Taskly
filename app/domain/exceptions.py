class DomainException(Exception):
    """Базовий виняток домену: від нього наслідуються всі інші."""


class ValidationException(DomainException):
    """Дані не пройшли перевірку: порожня назва, хибний розклад, некоректний ідентифікатор."""


class InvalidTaskException(DomainException):
    """Дія над завданням неможлива в його поточному статусі."""
