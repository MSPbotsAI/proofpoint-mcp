from collections.abc import Callable

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .._json import dump_json_capped
from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def proofpoint_essentials_me_get_me() -> str:
        """Get metadata about the current Essentials API user; useful as a connectivity check."""
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        try:
            result = await client.get("/me")
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()
