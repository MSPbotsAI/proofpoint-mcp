"""Gateway credential middleware tests: missing-header 401, and header
values correctly reaching the per-request contextvars (no global-state
leakage across requests) for both wrapped Proofpoint products.
"""

import asyncio

from starlette.testclient import TestClient

from proofpoint_mcp.__main__ import _build_http_app
from proofpoint_mcp.config import Settings
from proofpoint_mcp.server import (
    GatewayTokenMiddleware,
    _essentials_creds_var,
    _tap_creds_var,
    create_mcp_server,
    get_essentials_client_from_context,
    get_tap_client_from_context,
)


def _make_app():
    settings = Settings()
    mcp = create_mcp_server(settings)
    return _build_http_app(mcp, settings), settings


def test_health_is_local_and_does_not_require_credentials():
    app, _ = _make_app()
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


def test_missing_both_credential_sets_returns_401_with_required_headers_listed():
    app, _ = _make_app()
    with TestClient(app) as client:
        resp = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
            headers={"Accept": "application/json, text/event-stream"},
        )
        assert resp.status_code == 401
        body = resp.json()
        required = " ".join(body["required_headers"])
        assert "X-Proofpoint-Tap-Service-Principal" in required
        assert "X-Proofpoint-Essentials-Username" in required


def test_tap_credentials_alone_reach_request_context_and_essentials_stays_none():
    settings = Settings()
    seen = {}

    async def fake_app(scope, receive, send):
        seen["tap"] = _tap_creds_var.get()
        seen["essentials"] = _essentials_creds_var.get()
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    middleware = GatewayTokenMiddleware(fake_app, settings)

    async def run():
        scope = {
            "type": "http",
            "path": "/mcp",
            "headers": [
                (b"x-proofpoint-tap-service-principal", b"principal-123"),
                (b"x-proofpoint-tap-service-secret", b"secret-456"),
            ],
        }

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            pass

        await middleware(scope, receive, send)

    asyncio.run(run())
    assert seen["tap"] == ("principal-123", "secret-456", settings.proofpoint_tap_base_url)
    assert seen["essentials"] is None
    # After the request completes, both contextvars must be reset — a fresh
    # get() outside any request context sees no leftover credential.
    assert _tap_creds_var.get() is None
    assert _essentials_creds_var.get() is None


def test_essentials_credentials_alone_reach_request_context_and_tap_stays_none():
    settings = Settings()
    seen = {}

    async def fake_app(scope, receive, send):
        seen["tap"] = _tap_creds_var.get()
        seen["essentials"] = _essentials_creds_var.get()
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    middleware = GatewayTokenMiddleware(fake_app, settings)

    async def run():
        scope = {
            "type": "http",
            "path": "/mcp",
            "headers": [
                (b"x-proofpoint-essentials-username", b"api-user"),
                (b"x-proofpoint-essentials-password", b"pw-789"),
                (b"x-proofpoint-essentials-base-url", b"us1.proofpointessentials.com"),
            ],
        }

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            pass

        await middleware(scope, receive, send)

    asyncio.run(run())
    assert seen["tap"] is None
    assert seen["essentials"] == ("api-user", "pw-789", "us1.proofpointessentials.com")
    assert _tap_creds_var.get() is None
    assert _essentials_creds_var.get() is None


def test_client_factories_return_none_without_context():
    assert get_tap_client_from_context() is None
    assert get_essentials_client_from_context() is None
