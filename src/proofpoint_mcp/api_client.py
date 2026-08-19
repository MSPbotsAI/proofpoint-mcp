import asyncio
import base64
from typing import Any

import httpx

from ._json import error_envelope

_TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_MAX_RETRIES = 3
_MAX_BACKOFF_SECONDS = 20.0

# One shared connection pool for the process lifetime. No credentials are ever
# stored on it — each client instance carries its own per-request auth headers
# (built from the caller's Header-supplied credentials), so sharing this pool
# across tenants/requests is safe. Request-level isolation is what actually
# keeps tenants apart (see server.py's contextvar-based credential isolation).
_http_client: httpx.AsyncClient | None = None


def _get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True)
    return _http_client


# status_code -> (error code, retryable). status_code 0 means a network/
# connection-level failure (no response at all).
_STATUS_TO_CODE: dict[int, tuple[str, bool]] = {
    0: ("upstream_error", True),
    400: ("invalid_argument", False),
    401: ("unauthorized", False),
    403: ("unauthorized", False),
    404: ("not_found", False),
    422: ("invalid_argument", False),
    429: ("rate_limited", True),
}


def _classify(status_code: int) -> tuple[str, bool]:
    if status_code in _STATUS_TO_CODE:
        return _STATUS_TO_CODE[status_code]
    if status_code >= 500:
        return "upstream_error", True
    return "invalid_argument", False


class ProofpointError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Proofpoint API error {status_code}: {message}")

    def to_envelope(self) -> str:
        code, retryable = _classify(self.status_code)
        return error_envelope(code, self.message, retryable)


class _BaseProofpointClient:
    """Shared request/retry/error-parsing plumbing for both Proofpoint clients.

    Reuses the module-level connection pool (see _get_http_client) across
    every call made through an instance, rather than opening a new connection
    per request. TAP and Essentials are two distinct Proofpoint products with
    different auth-header shapes and base URLs, so subclasses only need to
    set self._base_url and implement _headers().
    """

    _base_url: str

    def _headers(self) -> dict[str, str]:
        raise NotImplementedError

    def _clean_params(self, params: dict | None) -> dict:
        if not params:
            return {}
        return {k: v for k, v in params.items() if v is not None}

    async def get(self, path: str, params: dict | None = None) -> Any:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, params: dict | None = None, json_body: Any = None) -> Any:
        return await self._request("POST", path, params=params, json_body=json_body)

    async def put(self, path: str, params: dict | None = None, json_body: Any = None) -> Any:
        return await self._request("PUT", path, params=params, json_body=json_body)

    async def patch(self, path: str, params: dict | None = None, json_body: Any = None) -> Any:
        return await self._request("PATCH", path, params=params, json_body=json_body)

    async def delete(self, path: str, params: dict | None = None) -> Any:
        return await self._request("DELETE", path, params=params)

    async def _request(
        self, method: str, path: str, params: dict | None = None, json_body: Any = None
    ) -> Any:
        client = _get_http_client()
        url = f"{self._base_url}{path}"
        headers = self._headers()
        params = self._clean_params(params)

        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES + 1):
            try:
                resp = await client.request(
                    method, url, headers=headers, params=params, json=json_body
                )
            except httpx.RequestError as e:
                last_exc = e
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(min(2**attempt, _MAX_BACKOFF_SECONDS))
                    continue
                raise ProofpointError(0, f"{e or type(e).__name__} (url={url})") from e

            if resp.status_code in _RETRYABLE_STATUS and attempt < _MAX_RETRIES:
                delay = self._retry_delay(resp, attempt)
                await asyncio.sleep(delay)
                continue

            self._raise_for_status(resp)
            return self._parse_body(resp)

        # Unreachable in practice (loop always returns or raises above), but
        # keeps type checkers happy and guards against future edits.
        if last_exc:
            raise ProofpointError(0, f"{last_exc}") from last_exc
        raise ProofpointError(0, "request failed with no response")

    def _retry_delay(self, resp: httpx.Response, attempt: int) -> float:
        retry_after = resp.headers.get("Retry-After")
        if retry_after:
            try:
                return min(float(retry_after), _MAX_BACKOFF_SECONDS)
            except ValueError:
                pass
        return min(2**attempt, _MAX_BACKOFF_SECONDS)

    def _parse_body(self, resp: httpx.Response) -> Any:
        if not resp.content:
            return None
        try:
            return resp.json()
        except ValueError:
            return {"raw_response": resp.text}

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.status_code >= 400:
            try:
                detail = resp.json()
                if isinstance(detail, dict):
                    msg = detail.get("message") or detail.get("error") or str(detail)
                else:
                    msg = str(detail)
            except ValueError:
                msg = resp.text
            raise ProofpointError(resp.status_code, str(msg))


class ProofpointTapClient(_BaseProofpointClient):
    """Async httpx client wrapping the Proofpoint TAP (Targeted Attack Protection) API.

    Auth is HTTP Basic with a service principal + secret, per Proofpoint's own
    documented format (Threat Insight Dashboard -> Settings -> Connected
    Applications -> Service Credentials).
    """

    def __init__(self, service_principal: str, service_secret: str, base_url: str):
        self._service_principal = service_principal
        self._service_secret = service_secret
        self._base_url = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        token = base64.b64encode(
            f"{self._service_principal}:{self._service_secret}".encode()
        ).decode()
        return {
            "Authorization": f"Basic {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }


class ProofpointEssentialsClient(_BaseProofpointClient):
    """Async httpx client wrapping the Proofpoint Essentials Interface API.

    Auth is a registered Essentials username/password sent on every request
    as the X-User / X-Password headers (Proofpoint's own documented format —
    not HTTP Basic Auth). The API is instance-specific (e.g.
    us1.proofpointessentials.com, eu1.proofpointessentials.com); base_url is
    supplied per-request since it varies per tenant/Organization.
    """

    def __init__(self, username: str, password: str, base_url: str):
        self._username = username
        self._password = password
        base_url = base_url.rstrip("/")
        if not base_url.startswith("http://") and not base_url.startswith("https://"):
            base_url = f"https://{base_url}"
        self._base_url = f"{base_url}/api/v1"

    def _headers(self) -> dict[str, str]:
        return {
            "X-User": self._username,
            "X-Password": self._password,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
