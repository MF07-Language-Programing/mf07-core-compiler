"""Path utilities exposed as mf.path for CorpLang programs."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List


def _ensure_path(path: str | os.PathLike | None) -> Path:
    if path is None:
        raise ValueError("path must be provided")
    if isinstance(path, Path):
        return path
    return Path(str(path)).expanduser()


def join(*parts: str) -> str:
    cleaned = [str(part) for part in parts if part not in (None, "")]
    if not cleaned:
        return ""
    return str(Path(cleaned[0]).joinpath(*cleaned[1:]))


def join_all(parts: Iterable[str]) -> str:
    cleaned = [str(part) for part in parts if part not in (None, "")]
    if not cleaned:
        return ""
    return str(Path(cleaned[0]).joinpath(*cleaned[1:]))


def basename(path: str) -> str:
    try:
        return _ensure_path(path).name
    except Exception:
        return ""


def dirname(path: str) -> str:
    try:
        return str(_ensure_path(path).parent)
    except Exception:
        return ""


def stem(path: str) -> str:
    try:
        return _ensure_path(path).stem
    except Exception:
        return ""


def extname(path: str) -> str:
    try:
        return _ensure_path(path).suffix
    except Exception:
        return ""


def parts(path: str) -> List[str]:
    try:
        return [str(part) for part in _ensure_path(path).parts]
    except Exception:
        return []


def split(path: str) -> List[str]:
    return parts(path)


def normalize(path: str) -> str:
    try:
        return os.path.normpath(str(_ensure_path(path)))
    except Exception:
        return ""


def resolve(path: str, base: str | None = None) -> str:
    try:
        target = _ensure_path(path)
        if base:
            target = _ensure_path(base) / target
        return str(target.resolve())
    except Exception:
        try:
            # Fallback without strict resolution
            target = _ensure_path(path)
            if base:
                target = _ensure_path(base) / target
            return str(target.absolute())
        except Exception:
            return ""


def relative_to(path: str, start: str | None = None) -> str:
    try:
        target = _ensure_path(path)
        base = _ensure_path(start) if start else Path.cwd()
        return str(target.relative_to(base))
    except Exception:
        try:
            return os.path.relpath(str(target), str(base))  # type: ignore[misc]
        except Exception:
            return ""


def is_absolute(path: str) -> bool:
    try:
        return _ensure_path(path).is_absolute()
    except Exception:
        return False


def match(path: str, pattern: str) -> bool:
    try:
        return _ensure_path(path).match(pattern)
    except Exception:
        return False


def common_path(paths: Iterable[str]) -> str:
    try:
        cleaned = [str(_ensure_path(p)) for p in paths]
        if not cleaned:
            return ""
        return os.path.commonpath(cleaned)
    except Exception:
        return ""


def with_suffix(path: str, suffix: str) -> str:
    try:
        return str(_ensure_path(path).with_suffix(suffix))
    except Exception:
        return ""


def expanduser(path: str) -> str:
    try:
        return str(_ensure_path(path))
    except Exception:
        return ""


def to_posix(path: str) -> str:
    try:
        return _ensure_path(path).as_posix()
    except Exception:
        return ""


def to_windows(path: str) -> str:
    try:
        return str(_ensure_path(path))
    except Exception:
        return ""


def cwd() -> str:
    return str(Path.cwd())


def home() -> str:
    return str(Path.home())


def drive(path: str) -> str:
    try:
        return _ensure_path(path).drive
    except Exception:
        return ""
