import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointTapClient, ProofpointError
from ._common import NO_TAP_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointTapClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_tap_threats_get_by_id(threat_id: str) -> str:
        """Get detailed information about a specific threat by its threat ID. Returns threat type, classification, and associated indicators. Live-verified: returns 401 (route recognized) with a placeholder threat id and credentials. The official Threats API doc page is login-gated so its full parameter/response schema could not be independently reviewed beyond this live-verified endpoint.

        API: GET /v2/threat/summary/{threat_id}

        Args:
            threat_id: Required. The threat ID (SHA256 hash or Proofpoint threat ID)
        """
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        path = f"/v2/threat/summary/{threat_id}"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
