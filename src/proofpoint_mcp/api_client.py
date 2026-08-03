import base64
from typing import Any

import httpx


class ProofpointError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"Proofpoint API error {status_code}: {message}")


def _clean_params(params: dict | None) -> dict:
    if not params:
        return {}
    return {k: v for k, v in params.items() if v is not None}


def _parse_body(resp: httpx.Response) -> Any:
    if not resp.content:
        return None
    try:
        return resp.json()
    except ValueError:
        return {"raw_response": resp.text}


def _raise_for_status(resp: httpx.Response) -> None:
    if resp.status_code >= 400:
        try:
            detail = resp.json()
        except ValueError:
            detail = None
        msg = resp.text
        if isinstance(detail, dict):
            msg = detail.get("message") or detail.get("error") or str(detail)
        elif detail is not None:
            msg = str(detail)
        raise ProofpointError(resp.status_code, str(msg))


class ProofpointTapClient:
    """Async httpx client wrapping the Proofpoint TAP (Targeted Attack Protection) API.

    Auth is HTTP Basic with a service principal + secret, per Proofpoint's own
    documented format (Settings > Connected Applications > Service Credentials
    in the Threat Insight Dashboard).
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

    async def get(self, path: str, params: dict | None = None) -> Any:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, params: dict | None = None, json_body: Any = None) -> Any:
        return await self._request("POST", path, params=params, json_body=json_body)

    async def delete(self, path: str, params: dict | None = None) -> Any:
        return await self._request("DELETE", path, params=params)

    async def _request(
        self, method: str, path: str, params: dict | None = None, json_body: Any = None
    ) -> Any:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.request(
                    method,
                    f"{self._base_url}{path}",
                    headers=self._headers(),
                    params=_clean_params(params),
                    json=json_body,
                )
            except httpx.RequestError as e:
                raise ProofpointError(
                    0, f"{e or type(e).__name__} (url={self._base_url}{path})"
                ) from e
            _raise_for_status(resp)
            return _parse_body(resp)


class ProofpointEssentialsClient:
    """Async httpx client wrapping the Proofpoint Essentials Interface API.

    Auth is a registered Essentials username/password sent on every request
    as the `X-User` / `X-Password` headers (Proofpoint's own documented
    format — not HTTP Basic Auth). The API is instance-specific (e.g.
    us1.proofpointessentials.com, eu1.proofpointessentials.com); base_url is
    supplied per-request since it varies per Organization.
    """

    def __init__(self, username: str, password: str, base_url: str):
        self._username = username
        self._password = password
        base_url = base_url.rstrip("/")
        if not base_url.startswith("http://") and not base_url.startswith("https://"):
            base_url = f"https://{base_url}"
        self._base_url = base_url

    def _headers(self) -> dict[str, str]:
        return {
            "X-User": self._username,
            "X-Password": self._password,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

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
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.request(
                    method,
                    f"{self._base_url}/api/v1{path}",
                    headers=self._headers(),
                    params=_clean_params(params),
                    json=json_body,
                )
            except httpx.RequestError as e:
                raise ProofpointError(
                    0, f"{e or type(e).__name__} (url={self._base_url}/api/v1{path})"
                ) from e
            _raise_for_status(resp)
            return _parse_body(resp)
