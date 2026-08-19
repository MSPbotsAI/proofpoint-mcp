from collections.abc import Callable
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .._json import dump_json_capped
from ..api_client import ProofpointError, ProofpointTapClient
from ._common import NO_TAP_TOKEN

# Proofpoint's own docs give no maximum for this endpoint's `size` (unlike the
# sibling top-clickers endpoint, which documents a max of 200) — fall back to
# the SOP's default/hard-cap ceiling rather than trusting an undocumented
# vendor default (which is 1000, too large for a token-bounded tool result).
_DEFAULT_SIZE = 50
_MAX_SIZE = 200


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointTapClient | None]) -> None:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def proofpoint_tap_people_get_vap(
        window: Annotated[
            str, Field(description="Days of data to retrieve. Accepted values: 14, 30, or 90.")
        ],
        size: Annotated[
            str | None,
            Field(
                description=f"Max VAPs to return, ordered by attackIndex. Default {_DEFAULT_SIZE}, hard-capped at {_MAX_SIZE}."
            ),
        ] = None,
        page: Annotated[
            str | None, Field(description="Page of results, in multiples of size. Default 1.")
        ] = None,
    ) -> str:
        """List an org's Very Attacked People (VAP) and their attack-index risk scores.

        Use for "who are our most-targeted people" questions.
        """
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        try:
            size_val = min(int(size), _MAX_SIZE) if size is not None else _DEFAULT_SIZE
        except ValueError:
            size_val = _DEFAULT_SIZE
        params = {"window": window, "size": str(size_val), "page": page}
        try:
            result = await client.get("/v2/people/vap", params=params)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()
