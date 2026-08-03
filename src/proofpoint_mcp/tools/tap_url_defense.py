import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointTapClient, ProofpointError
from ._common import NO_TAP_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointTapClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_tap_url_defense_decode(body: dict) -> str:
        """Decode one or more Proofpoint URL Defense rewritten URLs back to the original URLs. Per official docs this endpoint works unauthenticated too (reduced field set), but this server always sends the configured TAP credentials.

        API: POST /v2/url/decode

        Args:
            body: Required. Array of Proofpoint-encoded URLs to decode
        """
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        params = {}
        try:
            result = await client.post("/v2/url/decode", params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
