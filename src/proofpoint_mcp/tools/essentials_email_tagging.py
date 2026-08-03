import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_essentials_email_tagging_delete_email_tagging_exemptions(domain: str) -> str:
        """Delete specified Email Tagging Exempt Senders for an Organization.

        API: DELETE /orgs/{domain}/email-tagging/exemptions

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/email-tagging/exemptions"
        params = {}
        try:
            result = await client.delete(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_email_tagging_get(domain: str) -> str:
        """Read email tagging settings for an Organization.

        API: GET /orgs/{domain}/email-tagging

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/email-tagging"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_email_tagging_get_email_tagging_exemptions(domain: str) -> str:
        """Retrieve Email Tagging Exempt Senders.

        API: GET /orgs/{domain}/email-tagging/exemptions

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/email-tagging/exemptions"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_email_tagging_patch(domain: str, body: dict) -> str:
        """Update a specific email tagging setting for an Organization.

        API: PATCH /orgs/{domain}/email-tagging

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. Email tagging data (all fields optional)
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/email-tagging"
        params = {}
        try:
            result = await client.patch(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_email_tagging_post_email_tagging_exemptions(domain: str, body: dict) -> str:
        """Create Email Tagging Exempt Senders for an Organization.

        API: POST /orgs/{domain}/email-tagging/exemptions

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. Email tagging data (all fields optional)
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/email-tagging/exemptions"
        params = {}
        try:
            result = await client.post(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_email_tagging_put(domain: str, body: dict) -> str:
        """Update email tagging settings for an Organization.

        API: PUT /orgs/{domain}/email-tagging

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. Email tagging data
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/email-tagging"
        params = {}
        try:
            result = await client.put(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
