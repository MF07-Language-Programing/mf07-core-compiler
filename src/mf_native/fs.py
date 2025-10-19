"""File system helpers exposed to CorpLang through the mf.fs namespace."""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def _ensure_path(path: Any) -> Path:
    if path is None:
        raise ValueError("path must be provided")
    if isinstance(path, Path):
        return path
    return Path(str(path)).expanduser()


def _timestamp(value: float) -> str:
    try:
        return datetime.utcfromtimestamp(value).strftime(ISO_FORMAT)
    except Exception:
        return ""


def _success(**payload: Any) -> Dict[str, Any]:
    payload["ok"] = True
    return payload


def _failure(path: Optional[Path], message: str) -> Dict[str, Any]:
    return {"ok": False, "error": message, "path": str(path) if path else ""}


def read_text(path: Any, encoding: Optional[str] = None) -> Dict[str, Any]:
    encoding = encoding or "utf-8"
    file_path: Optional[Path] = None
    try:
        file_path = _ensure_path(path)
        content = file_path.read_text(encoding=encoding)
        return _success(path=str(file_path), content=content, encoding=encoding)
    except Exception as exc:
        return _failure(file_path, str(exc))


def write_text(
    path: Any,
    content: Any,
    encoding: Optional[str] = None,
    append: bool = False,
    create_dirs: bool = True,
) -> Dict[str, Any]:
    encoding = encoding or "utf-8"
    file_path: Optional[Path] = None
    try:
        file_path = _ensure_path(path)
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with file_path.open(mode, encoding=encoding, newline="") as handle:
            handle.write("" if content is None else str(content))
        return _success(path=str(file_path), encoding=encoding, appended=append)
    except Exception as exc:
        return _failure(file_path, str(exc))


def append_text(
    path: Any, content: Any, encoding: Optional[str] = None
) -> Dict[str, Any]:
    return write_text(path, content, encoding=encoding, append=True)


def read_json(path: Any, encoding: Optional[str] = None) -> Dict[str, Any]:
    result = read_text(path, encoding=encoding)
    if not result.get("ok"):
        return result
    try:
        data = json.loads(result["content"])
        return _success(path=result.get("path", ""), data=data)
    except Exception as exc:
        return _failure(Path(result.get("path", "")), str(exc))


def write_json(
    path: Any,
    data: Any,
    encoding: Optional[str] = None,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> Dict[str, Any]:
    encoding = encoding or "utf-8"
    file_path: Optional[Path] = None
    try:
        file_path = _ensure_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
        file_path.write_text(payload, encoding=encoding)
        return _success(path=str(file_path), encoding=encoding)
    except Exception as exc:
        return _failure(file_path, str(exc))


def read_bytes(path: Any) -> Dict[str, Any]:
    file_path: Optional[Path] = None
    try:
        file_path = _ensure_path(path)
        content = file_path.read_bytes()
        return _success(path=str(file_path), content=list(content))
    except Exception as exc:
        return _failure(file_path, str(exc))


def write_bytes(path: Any, data: Iterable[int]) -> Dict[str, Any]:
    file_path: Optional[Path] = None
    try:
        file_path = _ensure_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = bytes(byte & 0xFF for byte in data)
        file_path.write_bytes(payload)
        return _success(path=str(file_path), size=len(payload))
    except Exception as exc:
        return _failure(file_path, str(exc))


def exists(path: Any) -> bool:
    try:
        return _ensure_path(path).exists()
    except Exception:
        return False


def is_file(path: Any) -> bool:
    try:
        return _ensure_path(path).is_file()
    except Exception:
        return False


def is_dir(path: Any) -> bool:
    try:
        return _ensure_path(path).is_dir()
    except Exception:
        return False


def make_dir(path: Any, parents: bool = True) -> Dict[str, Any]:
    directory: Optional[Path] = None
    try:
        directory = _ensure_path(path)
        directory.mkdir(parents=parents, exist_ok=True)
        return _success(path=str(directory))
    except Exception as exc:
        return _failure(directory, str(exc))


def touch(path: Any) -> Dict[str, Any]:
    file_path: Optional[Path] = None
    try:
        file_path = _ensure_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch(exist_ok=True)
        return _success(path=str(file_path))
    except Exception as exc:
        return _failure(file_path, str(exc))


def remove(path: Any, recursive: bool = False) -> Dict[str, Any]:
    target: Optional[Path] = None
    try:
        target = _ensure_path(path)
        if not target.exists():
            return _success(path=str(target), removed=False)
        if target.is_dir():
            if recursive:
                shutil.rmtree(target)
            else:
                target.rmdir()
        else:
            target.unlink()
        return _success(path=str(target), removed=True)
    except Exception as exc:
        return _failure(target, str(exc))


def list_dir(path: Any, recursive: bool = False) -> Dict[str, Any]:
    base: Optional[Path] = None
    try:
        base = _ensure_path(path)
        entries: List[Dict[str, Any]] = []
        if recursive:
            for root, dirs, files in os.walk(base):
                root_path = Path(root)
                for directory in dirs:
                    current = root_path / directory
                    entries.append(
                        {
                            "name": directory,
                            "path": str(current),
                            "type": "dir",
                            "size": None,
                        }
                    )
                for file_name in files:
                    current = root_path / file_name
                    entries.append(
                        {
                            "name": file_name,
                            "path": str(current),
                            "type": "file",
                            "size": current.stat().st_size,
                        }
                    )
        else:
            for child in base.iterdir():
                entry_type = "dir" if child.is_dir() else "file"
                size = child.stat().st_size if child.is_file() else None
                entries.append(
                    {
                        "name": child.name,
                        "path": str(child),
                        "type": entry_type,
                        "size": size,
                    }
                )
        return _success(path=str(base), entries=entries, recursive=recursive)
    except Exception as exc:
        return _failure(base, str(exc))


def copy(src: Any, dest: Any, overwrite: bool = True) -> Dict[str, Any]:
    src_path: Optional[Path] = None
    dest_path: Optional[Path] = None
    try:
        src_path = _ensure_path(src)
        dest_path = _ensure_path(dest)
        if dest_path.exists():
            if overwrite:
                if dest_path.is_dir() and not src_path.is_dir():
                    shutil.rmtree(dest_path)
                elif dest_path.is_file():
                    dest_path.unlink()
            else:
                return _failure(dest_path, "destination already exists")
        if src_path.is_dir():
            shutil.copytree(src_path, dest_path)
        else:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)
        return _success(source=str(src_path), destination=str(dest_path))
    except Exception as exc:
        return _failure(dest_path or src_path, str(exc))


def move(src: Any, dest: Any, overwrite: bool = True) -> Dict[str, Any]:
    src_path: Optional[Path] = None
    dest_path: Optional[Path] = None
    try:
        src_path = _ensure_path(src)
        dest_path = _ensure_path(dest)
        if dest_path.exists():
            if overwrite:
                if dest_path.is_dir():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()
            else:
                return _failure(dest_path, "destination already exists")
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dest_path))
        return _success(source=str(src_path), destination=str(dest_path))
    except Exception as exc:
        return _failure(dest_path or src_path, str(exc))


def stat(path: Any) -> Dict[str, Any]:
    target: Optional[Path] = None
    try:
        target = _ensure_path(path)
        info = target.stat()
        payload = {
            "size": info.st_size,
            "modified": _timestamp(info.st_mtime),
            "created": _timestamp(info.st_ctime),
            "accessed": _timestamp(info.st_atime),
            "is_dir": target.is_dir(),
            "is_file": target.is_file(),
            "path": str(target),
        }
        return _success(info=payload)
    except Exception as exc:
        return _failure(target, str(exc))


def glob(path: Any, pattern: str) -> Dict[str, Any]:
    base: Optional[Path] = None
    try:
        base = _ensure_path(path)
        matches = [str(p) for p in base.glob(pattern)]
        return _success(path=str(base), matches=matches)
    except Exception as exc:
        return _failure(base, str(exc))


def walk(path: Any) -> Dict[str, Any]:
    base: Optional[Path] = None
    try:
        base = _ensure_path(path)
        entries: List[Dict[str, Any]] = []
        for root, dirs, files in os.walk(base):
            entries.append(
                {
                    "path": root,
                    "directories": [str(Path(root) / d) for d in dirs],
                    "files": [str(Path(root) / f) for f in files],
                }
            )
        return _success(path=str(base), entries=entries)
    except Exception as exc:
        return _failure(base, str(exc))


def cwd() -> str:
    return str(Path.cwd())


def home() -> str:
    return str(Path.home())


def separator() -> str:
    return os.sep


def parent(path: Any) -> str:
    try:
        return str(_ensure_path(path).parent)
    except Exception:
        return ""
