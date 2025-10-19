import time
from typing import Optional, Any, Dict

import requests


class HttpClient:
    """HTTP client used by the interpreter to back mf.strict.https.request."""

    def __init__(self, base_url: str, defaults_headers: Optional[dict] = None):
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.defaults_headers: Dict[str, Any] = defaults_headers or {}

    def getUri(self) -> str:
        return self.base_url

    def getDefaultsHeaders(self) -> Dict[str, Any]:
        return self.defaults_headers

    def _merge_headers(self, custom: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        headers = dict(self.defaults_headers)
        if custom:
            headers.update({str(k): str(v) for k, v in custom.items()})
        return headers

    def _coerce_proxy(self, proxy: Any) -> Optional[Dict[str, str]]:
        if proxy is None:
            return None
        if isinstance(proxy, dict):
            return {str(k): str(v) for k, v in proxy.items()}
        if isinstance(proxy, str) and proxy:
            return {"http": proxy, "https": proxy}
        return None

    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not self.base_url:
            return path
        if not path:
            return self.base_url
        if path.startswith("/"):
            return f"{self.base_url}{path}"
        return f"{self.base_url}/{path}"

    def _success_payload(self, response: requests.Response) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "ok": response.ok,
            "status": response.status_code,
            "reason": response.reason or "",
            "url": response.url,
            "elapsed": response.elapsed.total_seconds() if response.elapsed else 0.0,
            "headers": dict(response.headers),
            "encoding": response.encoding,
            "content": list(response.content or b""),
        }
        text_value = response.text if response.text is not None else ""
        payload["text"] = text_value
        try:
            payload["json"] = response.json()
        except ValueError:
            payload["json"] = None
        return payload

    def _error_payload(self, exc: requests.RequestException) -> Dict[str, Any]:
        response = getattr(exc, "response", None)
        payload: Dict[str, Any] = {
            "ok": False,
            "status": getattr(response, "status_code", 0) or 0,
            "error": str(exc),
            "reason": getattr(response, "reason", ""),
            "url": getattr(response, "url", self.base_url),
            "headers": dict(getattr(response, "headers", {}) or {}),
            "elapsed": getattr(
                getattr(response, "elapsed", None), "total_seconds", lambda: 0.0
            )(),
            "content": list(getattr(response, "content", b"")),
            "text": getattr(response, "text", "") or "",
        }
        try:
            payload["json"] = response.json() if response else None
        except ValueError:
            payload["json"] = None
        return payload

    def execute(self, options: Dict[str, Any]) -> Dict[str, Any]:
        method = str(options.get("method", "GET")).upper()
        path = str(options.get("path", ""))
        timeout_value = options.get("timeout", 30)
        try:
            timeout = float(timeout_value)
        except (TypeError, ValueError):
            timeout = 30.0
        retries = int(options.get("retries", 0))
        params = options.get("params") or {}
        headers = self._merge_headers(options.get("headers"))
        json_payload = options.get("json")
        data_payload = options.get("data")
        text_payload = options.get("text")
        binary_payload = options.get("binary")
        auth = options.get("auth")
        verify = options.get("ssl_verify", True)
        proxies = self._coerce_proxy(options.get("proxy"))
        allow_redirects = bool(options.get("follow_redirects", True))
        stream = bool(options.get("stream", False))

        if text_payload is not None:
            data_payload = text_payload
        if binary_payload is not None:
            data_payload = bytes(int(b) & 0xFF for b in binary_payload)

        url = self._build_url(path)

        attempt = 0
        last_error: Optional[requests.RequestException] = None

        while attempt <= retries:
            attempt += 1
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_payload,
                    data=data_payload,
                    timeout=timeout,
                    allow_redirects=allow_redirects,
                    auth=auth,
                    verify=verify,
                    proxies=proxies,
                    stream=stream,
                )
                return self._success_payload(response)
            except requests.RequestException as exc:
                last_error = exc
                if attempt > retries:
                    break
                time.sleep(min(1.0 * attempt, 5.0))

        if last_error is None:
            return {
                "ok": False,
                "status": 0,
                "error": "Request failed",
                "url": url,
                "headers": {},
                "text": "",
                "content": [],
                "json": None,
                "elapsed": 0.0,
            }
        return self._error_payload(last_error)
