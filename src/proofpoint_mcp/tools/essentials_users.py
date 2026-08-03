import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_essentials_users_delete_user(domain: str, user: str) -> str:
        """Delete a User.

        API: DELETE /orgs/{domain}/users/{user}

        Args:
            domain: Required. Any Domain associated with the Organization
            user: Required. Email address of a user
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users/{user}"
        params = {}
        try:
            result = await client.delete(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_users_get_user(domain: str, user: str) -> str:
        """Read a User belonging to an Organization.

        API: GET /orgs/{domain}/users/{user}

        Args:
            domain: Required. Any Domain associated with the Organization
            user: Required. Email address of a user
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users/{user}"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_users_get_users(domain: str) -> str:
        """Read all Users belonging to an Organization.

        API: GET /orgs/{domain}/users

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_users_post_user(domain: str, body: dict) -> str:
        """Create a new User. Batch POST supported with list of User objects.

        API: POST /orgs/{domain}/users

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. User data. May be a single object or a list of objects for batch creation
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users"
        params = {}
        try:
            result = await client.post(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_users_put_user(domain: str, user: str, body: dict) -> str:
        """Update a User belonging to an Organization.

        API: PUT /orgs/{domain}/users/{user}

        Args:
            domain: Required. Any Domain associated with the Organization
            user: Required. Email address of a user
            body: Required. User data
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users/{user}"
        params = {}
        try:
            result = await client.put(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
