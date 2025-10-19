from typing import Any, List, Tuple


def keys(o: Any) -> List[str]:
    if isinstance(o, dict):
        return list(o.keys())
    return [k for k in dir(o) if not k.startswith("__")]


def values(o: Any) -> List[Any]:
    if isinstance(o, dict):
        return list(o.values())
    return [getattr(o, k) for k in dir(o) if not k.startswith("__")]


def entries(o: Any) -> List[Tuple[str, Any]]:
    if isinstance(o, dict):
        return list(o.items())
    return [(k, getattr(o, k)) for k in dir(o) if not k.startswith("__")]


def clone(o: Any):
    import json as _json

    try:
        return _json.loads(_json.dumps(o))
    except Exception:
        return o
