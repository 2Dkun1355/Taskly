from datetime import datetime
from typing import Optional

INPUT_FORMAT = "%Y-%m-%d %H:%M"
INPUT_HINT = "YYYY-MM-DD HH:MM"


def parse_time(raw: str) -> Optional[datetime]:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw, INPUT_FORMAT).astimezone()
    except ValueError:
        raise ValueError(f"Time must look like {INPUT_HINT}")


def format_input(value: Optional[datetime]) -> str:
    return value.astimezone().strftime(INPUT_FORMAT) if value else ""


def describe_time(start: Optional[datetime], end: Optional[datetime]) -> str:
    if start and end:
        local_start, local_end = start.astimezone(), end.astimezone()
        if local_start.date() == local_end.date():
            return f"{local_start:%d %b %H:%M} - {local_end:%H:%M}"
        return f"{local_start:%d %b %H:%M} - {local_end:%d %b %H:%M}"
    if end:
        return f"due {end.astimezone():%d %b %H:%M}"
    return "no time"