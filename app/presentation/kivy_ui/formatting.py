from datetime import date

from application.queries.list_tasks import TaskSection
from domain.enums import TaskPriority, TaskStatus


SECTION_LABELS = {
    TaskSection.ALL_ACTIVE: "Усі активні",
    TaskSection.TODAY: "Сьогодні",
    TaskSection.UPCOMING: "Найближчі",
    TaskSection.ARCHIVE: "Архів",
}

PRIORITY_LABELS = {
    TaskPriority.LOW: "Низький",
    TaskPriority.MEDIUM: "Середній",
    TaskPriority.HIGH: "Високий",
}

STATUS_LABELS = {
    TaskStatus.PLANNED: "Заплановано",
    TaskStatus.COMPLETED: "Виконано",
    TaskStatus.NOT_COMPLETED: "Не виконано",
    TaskStatus.CANCELLED: "Скасовано",
}


def section_label(section: TaskSection) -> str:
    return SECTION_LABELS[section]


def priority_label(priority: TaskPriority) -> str:
    return PRIORITY_LABELS[priority]


def status_label(status: TaskStatus) -> str:
    return STATUS_LABELS[status]


def format_schedule(schedule):
    start, end = schedule.start_at, schedule.end_at
    if start is None and end is None:
        return "Без дати"

    today = date.today()

    def moment(value):
        local = value.astimezone()
        delta = (local.date() - today).days
        day = {0: "сьогодні", 1: "завтра", -1: "вчора"}.get(
            delta, local.strftime("%d.%m.%Y")
        )
        return f"{day} {local:%H:%M}"

    if start is None:
        return f"до {moment(end)}"
    if end is None:
        return f"{moment(start)}"
    return f"{moment(start)} — {end.astimezone():%H:%M}"
