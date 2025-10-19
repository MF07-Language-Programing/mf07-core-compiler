import json as _json


def parse(s: str):
    try:
        return _json.loads(s)
    except Exception:
        return None


def stringify(o) -> str:
    try:
        return _json.dumps(o, ensure_ascii=False)
    except Exception:
        return str(o)
