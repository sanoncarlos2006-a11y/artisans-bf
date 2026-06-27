from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONE = "Africa/Ouagadougou"


def _parse_opening_days(opening_days: str | None) -> set[int]:
    if not opening_days:
        return set()
    days: set[int] = set()
    for item in opening_days.split(","):
        item = item.strip()
        if item.isdigit():
            value = int(item)
            if 0 <= value <= 6:
                days.add(value)
    return days


def is_business_open_now(
    opening_days: str | None,
    open_time: str | None,
    close_time: str | None,
    is_temporarily_closed: bool = False,
) -> bool:
    if is_temporarily_closed:
        return False

    if not open_time or not close_time:
        return False

    now = datetime.now(ZoneInfo(TIMEZONE))
    current_day = now.weekday()  # 0=lundi ... 6=dimanche
    current_time = now.strftime("%H:%M")

    if current_day not in _parse_opening_days(opening_days):
        return False

    # Cas normal : 08:00 -> 18:00
    if open_time <= close_time:
        return open_time <= current_time <= close_time

    # Cas nuit : 20:00 -> 02:00
    return current_time >= open_time or current_time <= close_time


def get_open_status_label(
    opening_days: str | None,
    open_time: str | None,
    close_time: str | None,
    is_temporarily_closed: bool = False,
) -> str:
    if is_temporarily_closed:
        return "fermé temporairement"
    return "ouvert" if is_business_open_now(opening_days, open_time, close_time, is_temporarily_closed) else "fermé"
