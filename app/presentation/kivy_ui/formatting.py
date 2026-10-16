from datetime import date

PRIORITY_LABELS = {
    "LOW": "Низький",
    "MEDIUM": "Середній",
    "HIGH": "Високий",
}

STATE_LABELS = {
    "inbox": "Без дати",
    "overdue": "Прострочено",
    "planned": "Заплановано",
    "completed": "Виконано",
    "not_completed": "Не виконано",
    "cancelled": "Скасовано",
}

_WEEKDAYS = (
    "Понеділок", "Вівторок", "Середа", "Четвер",
    "П'ятниця", "Субота", "Неділя",
)

_MONTHS = (
    "січня", "лютого", "березня", "квітня", "травня", "червня",
    "липня", "серпня", "вересня", "жовтня", "листопада", "грудня",
)


def today_caption():
    """Сьогоднішня дата словами, наприклад «П'ятниця, 16 жовтня»."""
    today = date.today()
    return f"{_WEEKDAYS[today.weekday()]}, {today.day} {_MONTHS[today.month - 1]}"


def _day_word(day, today):
    """«Сьогодні», «Завтра», «Вчора» або дата."""
    delta = (day - today).days
    if delta == 0:
        return "Сьогодні"
    if delta == 1:
        return "Завтра"
    if delta == -1:
        return "Вчора"
    return day.strftime("%d.%m.%Y")


def _moment(value, today):
    """Момент часу в локальному часовому поясі, наприклад «Завтра 09:30»."""
    local = value.astimezone()
    return f"{_day_word(local.date(), today)} {local:%H:%M}"


def format_schedule(schedule):
    """Розклад завдання одним рядком. Дати показуються в локальному часі."""
    today = date.today()
    start, end = schedule.start_at, schedule.end_at

    if start is None and end is None:
        return "Без дати"

    if start is not None and end is not None:
        start_local, end_local = start.astimezone(), end.astimezone()
        if start_local.date() == end_local.date():
            return f"{_moment(start, today)} — {end_local:%H:%M}"
        return f"{_moment(start, today)} — {_moment(end, today)}"

    if end is not None:
        return f"До {_moment(end, today)}"

    return _moment(start, today)
