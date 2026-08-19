from collections.abc import Callable
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .._json import dump_json_capped
from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN

_DOMAIN_DESC = "Any domain already associated with the Essentials organization."
_USER_DESC = "Email address of the user."


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True))
    async def proofpoint_essentials_users_delete_user(
        domain: Annotated[str, Field(description=_DOMAIN_DESC)],
        user: Annotated[str, Field(description=_USER_DESC)],
    ) -> str:
        """Permanently delete a user from an Essentials organization. Irreversible."""
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users/{user}"
        try:
            result = await client.delete(path)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def proofpoint_essentials_users_get_user(
        domain: Annotated[str, Field(description=_DOMAIN_DESC)],
        user: Annotated[str, Field(description=_USER_DESC)],
    ) -> str:
        """Get one user belonging to an Essentials organization."""
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users/{user}"
        try:
            result = await client.get(path)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def proofpoint_essentials_users_get_users(
        domain: Annotated[str, Field(description=_DOMAIN_DESC)],
    ) -> str:
        """List all users belonging to an Essentials organization."""
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users"
        try:
            result = await client.get(path)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=False))
    async def proofpoint_essentials_users_post_user(
        domain: Annotated[str, Field(description=_DOMAIN_DESC)],
        body: Annotated[
            dict,
            Field(description="User data to create. A list of user objects creates a batch."),
        ],
    ) -> str:
        """Create one or more users under an Essentials organization (batch supported)."""
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users"
        try:
            result = await client.post(path, json_body=body)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True))
    async def proofpoint_essentials_users_put_user(
        domain: Annotated[str, Field(description=_DOMAIN_DESC)],
        user: Annotated[str, Field(description=_USER_DESC)],
        body: Annotated[dict, Field(description="User data to update.")],
    ) -> str:
        """Update an existing user's fields in an Essentials organization."""
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users/{user}"
        try:
            result = await client.put(path, json_body=body)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()
