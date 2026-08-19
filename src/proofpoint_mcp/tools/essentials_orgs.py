from collections.abc import Callable
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .._json import dump_json_capped
from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN

_DOMAIN_DESC = "Any domain already associated with the Essentials organization."


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:
    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def proofpoint_essentials_orgs_get_org(
        domain: Annotated[str, Field(description=_DOMAIN_DESC)],
    ) -> str:
        """Get an Essentials organization's settings and metadata."""
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}"
        try:
            result = await client.get(path)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True))
    async def proofpoint_essentials_orgs_patch_org(
        domain: Annotated[str, Field(description=_DOMAIN_DESC)],
        body: Annotated[
            dict, Field(description="One or more organization fields to update.")
        ],
    ) -> str:
        """Update one or more fields on an existing Essentials organization."""
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}"
        try:
            result = await client.patch(path, json_body=body)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=False))
    async def proofpoint_essentials_orgs_post_org(
        domain: Annotated[str, Field(description=_DOMAIN_DESC)],
        body: Annotated[
            dict, Field(description="Organization data to create. A list creates a batch.")
        ],
    ) -> str:
        """Create a new Essentials organization (batch supported)."""
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/orgs"
        try:
            result = await client.post(path, json_body=body)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()
