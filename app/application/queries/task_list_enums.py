from enum import StrEnum


class TaskSection(StrEnum):
    """Розділ списку завдань."""

    ALL = "all"
    TODAY = "today"
    UPCOMING = "upcoming"
    INBOX = "inbox"
    ARCHIVE = "archive"

    @property
    def label(self) -> str:
        return {
            TaskSection.ALL: "Усі активні",
            TaskSection.TODAY: "Сьогодні",
            TaskSection.UPCOMING: "Найближчі",
            TaskSection.INBOX: "Без дати",
            TaskSection.ARCHIVE: "Архів",
        }[self]


class ArchiveFilter(StrEnum):
    """Фільтр статусу архівних завдань."""

    ALL = "all"
    COMPLETED = "completed"
    NOT_COMPLETED = "not_completed"
    CANCELLED = "cancelled"

    @property
    def label(self) -> str:
        return {
            ArchiveFilter.ALL: "Усі",
            ArchiveFilter.COMPLETED: "Виконані",
            ArchiveFilter.NOT_COMPLETED: "Не виконані",
            ArchiveFilter.CANCELLED: "Скасовані",
        }[self]
