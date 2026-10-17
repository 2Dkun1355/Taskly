from datetime import datetime, timedelta

from domain.value_objects.schedule import Schedule
from presentation.kivy_ui.formatting import format_schedule


def test_format_schedule_without_dates():
    assert format_schedule(Schedule()) == "Без дати"


def test_format_schedule_formats_deadline():
    now = datetime.now().astimezone().replace(hour=9, minute=0, second=0, microsecond=0)
    result = format_schedule(Schedule(end_at=now + timedelta(hours=1)))

    assert result.startswith("До Сьогодні ")


def test_format_schedule_formats_start_only():
    now = datetime.now().astimezone().replace(hour=9, minute=0, second=0, microsecond=0)
    result = format_schedule(Schedule(start_at=now + timedelta(hours=1)))

    assert result.startswith("Сьогодні ")


def test_format_schedule_formats_same_day_interval():
    now = datetime.now().astimezone().replace(hour=9, minute=0, second=0, microsecond=0)
    result = format_schedule(
        Schedule(
            start_at=now + timedelta(hours=1),
            end_at=now + timedelta(hours=2),
        )
    )

    assert " — " in result
    assert result.count(":") == 2


def test_format_schedule_formats_interval_across_days():
    now = datetime.now().astimezone().replace(hour=9, minute=0, second=0, microsecond=0)
    result = format_schedule(
        Schedule(
            start_at=now + timedelta(days=1),
            end_at=now + timedelta(days=2),
        )
    )

    assert "Завтра" in result
    assert "." in result
    assert " — " in result
