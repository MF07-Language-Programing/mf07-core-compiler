"""Low-level socket helpers exposed through the mf.connections namespace."""

from __future__ import annotations

import socket
from typing import Any, Dict, Optional
from uuid import uuid4


_connections: Dict[str, socket.socket] = {}
_servers: Dict[str, socket.socket] = {}


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def _success(**payload: Any) -> Dict[str, Any]:
    payload["ok"] = True
    return payload


def _failure(message: str, **extra: Any) -> Dict[str, Any]:
    data = {"ok": False, "error": message}
    data.update(extra)
    return data


def _ensure_timeout(value: Optional[Any]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _register_connection(sock: socket.socket) -> str:
    conn_id = _new_id("conn")
    _connections[conn_id] = sock
    return conn_id


def _register_server(sock: socket.socket) -> str:
    srv_id = _new_id("srv")
    _servers[srv_id] = sock
    return srv_id


def _pop_socket(identifier: str) -> Optional[socket.socket]:
    if identifier in _connections:
        return _connections.pop(identifier)
    if identifier in _servers:
        return _servers.pop(identifier)
    return None


def _get_socket(identifier: str) -> Optional[socket.socket]:
    if identifier in _connections:
        return _connections[identifier]
    if identifier in _servers:
        return _servers[identifier]
    return None


def _address_tuple(address: Any) -> Dict[str, Any]:
    if not address:
        return {"host": "", "port": 0}
    host, port = address
    return {"host": host or "", "port": int(port)}


def _encode_payload(data: Any, encoding: Optional[str]) -> bytes:
    if data is None:
        return b""
    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return bytes(data)
    if isinstance(data, list):
        return bytes(int(b) & 0xFF for b in data)
    text = str(data)
    codec = encoding or "utf-8"
    return text.encode(codec)


def _decode_payload(payload: bytes, encoding: Optional[str]) -> Dict[str, Any]:
    codec = encoding or "utf-8"
    text: Optional[str]
    try:
        text = payload.decode(codec)
    except Exception:
        text = None
    return {
        "bytes": list(payload),
        "text": text or "",
        "size": len(payload),
    }


def tcp_connect(host: str, port: Any, timeout: Optional[Any] = None) -> Dict[str, Any]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        timeout_value = _ensure_timeout(timeout)
        if timeout_value is not None:
            sock.settimeout(timeout_value)
        sock.connect((host, int(port)))
        conn_id = _register_connection(sock)
        return _success(
            id=conn_id,
            local=_address_tuple(sock.getsockname()),
            remote=_address_tuple(sock.getpeername()),
            timeout=timeout_value,
        )
    except Exception as exc:
        try:
            sock.close()  # type: ignore[name-defined]
        except Exception:
            pass
        return _failure(str(exc), id="")


def tcp_close(identifier: str) -> Dict[str, Any]:
    sock = _pop_socket(identifier)
    if sock is None:
        return _failure("connection not found", id=identifier)
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass
    try:
        sock.close()
    except Exception as exc:
        return _failure(str(exc), id=identifier)
    return _success(id=identifier)


def tcp_send(
    identifier: str, data: Any, encoding: Optional[str] = None
) -> Dict[str, Any]:
    sock = _get_socket(identifier)
    if sock is None:
        return _failure("connection not found", id=identifier)
    try:
        payload = _encode_payload(data, encoding)
        sock.sendall(payload)
        return _success(id=identifier, bytes=len(payload))
    except Exception as exc:
        return _failure(str(exc), id=identifier)


def tcp_receive(
    identifier: str,
    size: Any = None,
    encoding: Optional[str] = None,
) -> Dict[str, Any]:
    sock = _get_socket(identifier)
    if sock is None:
        return _failure("connection not found", id=identifier)
    try:
        buffer_size = 4096 if size is None else max(1, int(size))
        payload = sock.recv(buffer_size)
        if payload == b"":
            return _failure("connection closed", id=identifier, closed=True)
        decoded = _decode_payload(payload, encoding)
        return _success(id=identifier, **decoded)
    except Exception as exc:
        return _failure(str(exc), id=identifier)


def set_timeout(identifier: str, timeout: Any) -> Dict[str, Any]:
    sock = _get_socket(identifier)
    if sock is None:
        return _failure("connection not found", id=identifier)
    value = _ensure_timeout(timeout)
    if value is None:
        return _failure("invalid timeout", id=identifier)
    try:
        sock.settimeout(value)
        return _success(id=identifier, timeout=value)
    except Exception as exc:
        return _failure(str(exc), id=identifier)


def connection_info(identifier: str) -> Dict[str, Any]:
    sock = _get_socket(identifier)
    if sock is None:
        return _failure("connection not found", id=identifier)
    try:
        local = _address_tuple(sock.getsockname())
        remote = None
        try:
            remote = _address_tuple(sock.getpeername())
        except Exception:
            remote = None
        timeout = sock.gettimeout()
        return _success(id=identifier, local=local, remote=remote, timeout=timeout)
    except Exception as exc:
        return _failure(str(exc), id=identifier)


def tcp_listen(
    host: str,
    port: Any,
    backlog: Any = None,
    reuse_address: bool = True,
    timeout: Optional[Any] = None,
) -> Dict[str, Any]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if reuse_address:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        timeout_value = _ensure_timeout(timeout)
        if timeout_value is not None:
            sock.settimeout(timeout_value)
        sock.bind((host, int(port)))
        listen_backlog = 5 if backlog is None else max(1, int(backlog))
        sock.listen(listen_backlog)
        srv_id = _register_server(sock)
        return _success(
            id=srv_id,
            local=_address_tuple(sock.getsockname()),
            backlog=listen_backlog,
            timeout=timeout_value,
        )
    except Exception as exc:
        try:
            sock.close()  # type: ignore[name-defined]
        except Exception:
            pass
        return _failure(str(exc), id="")


def tcp_accept(identifier: str, timeout: Optional[Any] = None) -> Dict[str, Any]:
    server = _get_socket(identifier)
    if server is None:
        return _failure("server not found", id=identifier)
    try:
        timeout_value = _ensure_timeout(timeout)
        if timeout_value is not None:
            server.settimeout(timeout_value)
        conn, address = server.accept()
        conn_id = _register_connection(conn)
        return _success(
            server=identifier,
            id=conn_id,
            remote=_address_tuple(address),
            local=_address_tuple(conn.getsockname()),
        )
    except Exception as exc:
        return _failure(str(exc), id=identifier)


def tcp_shutdown(identifier: str, how: str = "both") -> Dict[str, Any]:
    sock = _get_socket(identifier)
    if sock is None:
        return _failure("connection not found", id=identifier)
    mapping = {
        "read": socket.SHUT_RD,
        "write": socket.SHUT_WR,
        "both": socket.SHUT_RDWR,
    }
    mode = mapping.get(how.lower(), socket.SHUT_RDWR)
    try:
        sock.shutdown(mode)
        return _success(id=identifier, mode=how.lower())
    except Exception as exc:
        return _failure(str(exc), id=identifier)


def is_tracked(identifier: str) -> bool:
    return identifier in _connections or identifier in _servers


def release_all() -> None:
    for key in list(_connections.keys()):
        try:
            _connections[key].close()
        finally:
            _connections.pop(key, None)
    for key in list(_servers.keys()):
        try:
            _servers[key].close()
        finally:
            _servers.pop(key, None)


__all__ = [
    "tcp_connect",
    "tcp_close",
    "tcp_send",
    "tcp_receive",
    "tcp_listen",
    "tcp_accept",
    "tcp_shutdown",
    "set_timeout",
    "connection_info",
    "is_tracked",
    "release_all",
]
