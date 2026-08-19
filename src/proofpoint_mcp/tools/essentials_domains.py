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
    async def proofpoint_essentials_domains_get_domain(
        domain: Annotated[str, Field(description=_DOMAIN_DESC)],
        target_domain: Annotated[str, Field(description="Name of the domain to retrieve.")],
    ) -> str:
        """Get one domain registered to an Essentials organization."""
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains/{target_domain}"
        try:
            result = await client.get(path)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def proofpoint_essentials_domains_get_domains(
        domain: Annotated[str, Field(description=_DOMAIN_DESC)],
    ) -> str:
        """List all domains registered to an Essentials organization."""
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains"
        try:
            result = await client.get(path)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=False))
    async def proofpoint_essentials_domains_post_domain(
        domain: Annotated[str, Field(description=_DOMAIN_DESC)],
        body: Annotated[
            dict, Field(description="Domain data to create. A list of domain objects creates a batch.")
        ],
    ) -> str:
        """Create one or more domains under an Essentials organization (batch supported)."""
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains"
        try:
            result = await client.post(path, json_body=body)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()
