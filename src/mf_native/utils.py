from typing import Any


def len_(o: Any) -> int:
    try:
        return len(o)
    except Exception:
        return 0


def typeof(o: Any) -> str:
    if o is None:
        return "null"
    return type(o).__name__


def is_null(o: Any) -> bool:
    return o is None
