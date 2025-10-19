import datetime
from typing import Optional
from zoneinfo import ZoneInfo

DEFAULT_TIMEZONE_ID = "America/Sao_Paulo"


def now(as_string: bool = False) -> str | datetime.datetime:
    """Get the current date and time as an ISO 8601 string in the default timezone."""
    return datetime.datetime.now()


def _get_default_timezone() -> Optional[ZoneInfo]:
    return None


def _datetime(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    microsecond: int = 0,
    tzinfo: ZoneInfo | None = None,
) -> datetime.datetime:
    """Create a datetime object in the default timezone."""
    if tzinfo is None:
        tzinfo = _get_default_timezone()
    try:
        return datetime.datetime(
            year, month, day, hour, minute, second, microsecond, tzinfo=tzinfo
        )
    except Exception:
        return datetime.datetime.min.replace(tzinfo=tzinfo)


def today(
    as_string: bool = False,
    tzinfo: ZoneInfo | None = None,
) -> str | datetime.datetime:
    """Get today's date as an ISO 8601 string in the default timezone."""
    if tzinfo is None:
        tzinfo = _get_default_timezone()
    today_date = datetime.datetime.now(tzinfo).date()
    if as_string:
        return today_date.isoformat()
    return datetime.datetime.combine(today_date, datetime.datetime.min.time(), tzinfo=tz)  # type: ignore[arg-type]


def from_timestamp(
    timestamp: float,
    as_string: bool = False,
    tzinfo: ZoneInfo | None = None,
) -> str | datetime.datetime:
    """Convert a UNIX timestamp to a datetime in the default timezone."""
    if tzinfo is None:
        tzinfo = _get_default_timezone()
    dt = datetime.datetime.fromtimestamp(timestamp, tzinfo)
    if as_string:
        return dt.isoformat()
    return dt


def to_timestamp(dt: datetime.datetime) -> float:
    """Convert a datetime to a UNIX timestamp."""
    if dt.tzinfo is None:
        dt.tzinfo = (
            _get_default_timezone()
        )  # pyright: ignore[reportAttributeAccessIssue]
    return dt.timestamp()


def format(dt: datetime.datetime, fmt: str) -> str:
    """Format a datetime object to a string based on the provided format."""
    try:
        return dt.strftime(fmt)
    except Exception:
        return ""


def parse(date_string: str, fmt: str) -> datetime.datetime | None:
    """Parse a date string into a datetime object based on the provided format."""
    try:
        return datetime.datetime.strptime(date_string, fmt)
    except Exception:
        return None
