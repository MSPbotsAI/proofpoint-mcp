import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_essentials_sender_lists_delete_group_lists(domain: str, group: str) -> str:
        """Delete sender lists for a Group.

        API: DELETE /orgs/{domain}/groups/{group}/sender-lists

        Args:
            domain: Required. Any Domain associated with the Organization
            group: Required. Identifier of a group
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/groups/{group}/sender-lists"
        params = {}
        try:
            result = await client.delete(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sender_lists_delete_sender_lists(domain: str) -> str:
        """Delete sender lists for an Organization.

        API: DELETE /orgs/{domain}/sender-lists

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/sender-lists"
        params = {}
        try:
            result = await client.delete(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sender_lists_delete_user_lists(domain: str, user: str) -> str:
        """Delete sender lists for a User.

        API: DELETE /orgs/{domain}/users/{user}/sender-lists

        Args:
            domain: Required. Any Domain associated with the Organization
            user: Required. Email address of a user
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users/{user}/sender-lists"
        params = {}
        try:
            result = await client.delete(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sender_lists_get_group_lists(domain: str, group_id: str) -> str:
        """Read sender lists for a Group.

        API: GET /orgs/{domain}/groups/{group}/sender-lists

        Args:
            domain: Required. Any Domain associated with the Organization
            group_id: Required. Identifier of a group. Can use group name or id, but using name will only return the first result
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/groups/{group}/sender-lists"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sender_lists_get_sender_lists(domain: str) -> str:
        """Read sender lists for an Organization.

        API: GET /orgs/{domain}/sender-lists

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/sender-lists"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sender_lists_get_user_lists(domain: str, user: str) -> str:
        """Read sender lists for a User.

        API: GET /orgs/{domain}/users/{user}/sender-lists

        Args:
            domain: Required. Any Domain associated with the Organization
            user: Required. Email address of a user
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users/{user}/sender-lists"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sender_lists_patch_group_sender_lists(domain: str, group: str, body: dict) -> str:
        """Update sender lists for a Group.

        API: PATCH /orgs/{domain}/groups/{group}/sender-lists

        Args:
            domain: Required. Any Domain associated with the Organization
            group: Required. Identifier of a group
            body: Required. Sender lists data. At least one list must be specified
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/groups/{group}/sender-lists"
        params = {}
        try:
            result = await client.patch(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sender_lists_patch_sender_lists(domain: str, body: dict) -> str:
        """Update sender lists for an Organization.

        API: PATCH /orgs/{domain}/sender-lists

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. Sender lists data. At least one list must be specified
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/sender-lists"
        params = {}
        try:
            result = await client.patch(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sender_lists_patch_user_sender_lists(domain: str, user: str, body: dict) -> str:
        """Update sender lists for a User.

        API: PATCH /orgs/{domain}/users/{user}/sender-lists

        Args:
            domain: Required. Any Domain associated with the Organization
            user: Required. Email address of a user
            body: Required. Sender lists data. At least one list must be specified
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users/{user}/sender-lists"
        params = {}
        try:
            result = await client.patch(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sender_lists_post_group_lists(domain: str, group: str, body: dict) -> str:
        """Update sender lists for a Group.

        API: POST /orgs/{domain}/groups/{group}/sender-lists

        Args:
            domain: Required. Any Domain associated with the Organization
            group: Required. Identifier of a group
            body: Required. Sender lists data. At least one list must be specified
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/groups/{group}/sender-lists"
        params = {}
        try:
            result = await client.post(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sender_lists_post_sender_lists(domain: str, body: dict) -> str:
        """Update sender lists for an Organization.

        API: POST /orgs/{domain}/sender-lists

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. Sender lists data. At least one list must be specified
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/sender-lists"
        params = {}
        try:
            result = await client.post(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sender_lists_post_user_lists(domain: str, user: str, body: dict) -> str:
        """Update sender lists for a User.

        API: POST /orgs/{domain}/users/{user}/sender-lists

        Args:
            domain: Required. Any Domain associated with the Organization
            user: Required. Email address of a user
            body: Required. Sender lists data. At least one list must be specified
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/users/{user}/sender-lists"
        params = {}
        try:
            result = await client.post(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
