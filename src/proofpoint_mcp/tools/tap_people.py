import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointTapClient, ProofpointError
from ._common import NO_TAP_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointTapClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_tap_people_get_vap(window: str, size: str | None = None, page: str | None = None) -> str:
        """Fetch the identities and attack index breakdown of Very Attacked People (VAP) within your organization for a given period. Live-verified: returns 401 (route recognized) with placeholder credentials.

        API: GET /v2/people/vap

        Args:
            window: Required. Days of data to retrieve. Accepted values: 14, 30, or 90 (per official People API doc).
            size: Optional. Max VAPs to return, ordered by attackIndex (default: 1000)
            page: Optional. Page of results, in multiples of size (default: 1)
        """
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        params = {"window": window, "size": size, "page": page}
        try:
            result = await client.get("/v2/people/vap", params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
