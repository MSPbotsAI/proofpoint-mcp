import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_essentials_me_get_me() -> str:
        """Read metadata about the currently logged in User.

        API: GET /me

        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        params = {}
        try:
            result = await client.get("/me", params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
