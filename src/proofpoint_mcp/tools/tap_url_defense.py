from collections.abc import Callable
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .._json import dump_json_capped
from ..api_client import ProofpointError, ProofpointTapClient
from ._common import NO_TAP_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointTapClient | None]) -> None:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def proofpoint_tap_url_defense_decode(
        body: Annotated[dict, Field(description="Array of Proofpoint-encoded URLs to decode.")],
    ) -> str:
        """Decode Proofpoint URL Defense rewritten URLs back to their original URLs."""
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        try:
            result = await client.post("/v2/url/decode", json_body=body)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()
