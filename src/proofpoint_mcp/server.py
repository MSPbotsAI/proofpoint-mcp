import contextvars
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from .api_client import ProofpointEssentialsClient, ProofpointTapClient
from .config import Settings

# Per-request credential isolation via contextvars.
# GatewayTokenMiddleware sets these before the MCP handler runs.
# Python asyncio copies context per task, so concurrent SSE connections are isolated.
#
# This server wraps TWO independent Proofpoint products (TAP and Essentials)
# with two different credential types. A caller only using one product's
# tools should not be forced to also supply the other product's unused
# credentials, so both credential sets are optional at the transport level —
# only a request supplying NEITHER set is rejected outright. Each tool's own
# client_factory returns None (-> a NO_*_TOKEN error string) if its specific
# credentials are missing, regardless of what the blanket gate allowed through.
_tap_creds_var: contextvars.ContextVar[tuple[str, str, str] | None] = contextvars.ContextVar(
    "proofpoint_tap_creds", default=None
)
_essentials_creds_var: contextvars.ContextVar[tuple[str, str, str] | None] = contextvars.ContextVar(
    "proofpoint_essentials_creds", default=None
)


def get_tap_client_from_context() -> ProofpointTapClient | None:
    creds = _tap_creds_var.get()
    if not creds:
        return None
    service_principal, service_secret, base_url = creds
    return ProofpointTapClient(service_principal, service_secret, base_url)


def get_essentials_client_from_context() -> ProofpointEssentialsClient | None:
    creds = _essentials_creds_var.get()
    if not creds:
        return None
    username, password, base_url = creds
    return ProofpointEssentialsClient(username, password, base_url)


class GatewayTokenMiddleware:
    """ASGI middleware.

    Reads whichever of the two Proofpoint credential sets are present:
      - X-Proofpoint-Tap-Service-Principal / X-Proofpoint-Tap-Service-Secret
        (+ optional X-Proofpoint-Tap-Base-Url, default tap-api-v2.proofpoint.com)
      - X-Proofpoint-Essentials-Username / X-Proofpoint-Essentials-Password
        + required X-Proofpoint-Essentials-Base-Url (per-tenant instance)

    Returns 401 on /mcp requests only if NEITHER credential set is present at
    all. A request with just one set populated is allowed through; calling a
    tool that needs the other, absent set returns that tool's own NO_*_TOKEN
    error string instead of a transport-level 401.
    """

    def __init__(self, app: ASGIApp, settings: Settings):
        self.app = app
        self.settings = settings

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if not path.startswith("/mcp"):
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        tap_principal = request.headers.get("x-proofpoint-tap-service-principal")
        tap_secret = request.headers.get("x-proofpoint-tap-service-secret")
        tap_base_url = request.headers.get("x-proofpoint-tap-base-url") or self.settings.proofpoint_tap_base_url
        has_tap = bool(tap_principal and tap_secret)

        ess_user = request.headers.get("x-proofpoint-essentials-username")
        ess_password = request.headers.get("x-proofpoint-essentials-password")
        ess_base_url = request.headers.get("x-proofpoint-essentials-base-url")
        has_essentials = bool(ess_user and ess_password and ess_base_url)

        if not has_tap and not has_essentials:
            response = JSONResponse(
                {
                    "error": "Missing credentials",
                    "message": (
                        "This server requires either the TAP credential set "
                        "(X-Proofpoint-Tap-Service-Principal + "
                        "X-Proofpoint-Tap-Service-Secret) or the Essentials "
                        "credential set (X-Proofpoint-Essentials-Username + "
                        "X-Proofpoint-Essentials-Password + "
                        "X-Proofpoint-Essentials-Base-Url) — at least one is required"
                    ),
                    "required_headers": [
                        "X-Proofpoint-Tap-Service-Principal + X-Proofpoint-Tap-Service-Secret",
                        "OR X-Proofpoint-Essentials-Username + X-Proofpoint-Essentials-Password + X-Proofpoint-Essentials-Base-Url",
                    ],
                    "optional_headers": ["X-Proofpoint-Tap-Base-Url"],
                },
                status_code=401,
            )
            await response(scope, receive, send)
            return

        tap_token = _tap_creds_var.set((tap_principal, tap_secret, tap_base_url) if has_tap else None)
        ess_token = _essentials_creds_var.set(
            (ess_user, ess_password, ess_base_url) if has_essentials else None
        )
        try:
            await self.app(scope, receive, send)
        finally:
            _tap_creds_var.reset(tap_token)
            _essentials_creds_var.reset(ess_token)


def create_mcp_server(settings: Settings) -> FastMCP:
    """Build the FastMCP server instance and register all Proofpoint tools."""
    # DNS-rebinding protection is a browser-oriented safeguard that rejects
    # non-localhost Host headers with 421. Disable it so the server works
    # correctly behind a reverse proxy or docker network.
    mcp = FastMCP(
        name="proofpoint-mcp",
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )

    tap_client_factory: Callable[[], ProofpointTapClient | None] = get_tap_client_from_context
    essentials_client_factory: Callable[[], ProofpointEssentialsClient | None] = (
        get_essentials_client_from_context
    )

    from .tools import (
        essentials_domains,
        essentials_me,
        essentials_orgs,
        essentials_users,
        tap_people,
        tap_tap,
        tap_url_defense,
    )

    for mod in (
        tap_people,
        tap_tap,
        tap_url_defense,
    ):
        mod.register(mcp, tap_client_factory)

    for mod in (
        essentials_domains,
        essentials_me,
        essentials_orgs,
        essentials_users,
    ):
        mod.register(mcp, essentials_client_factory)

    return mcp
