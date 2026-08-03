import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_essentials_sync_exemptions_delete_all_azure_exemptions(domain: str) -> str:
        """Delete all organizations Sync Exemptions.

        API: DELETE /orgs/{domain}/settings/azure/exemptions

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/settings/azure/exemptions"
        params = {}
        try:
            result = await client.delete(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sync_exemptions_delete_azure_exemptions(domain: str, user: str) -> str:
        """Delete one Sync Exemption belonging to organization.

        API: DELETE /orgs/{domain}/settings/azure/exemptions/{user}

        Args:
            domain: Required. Any Domain associated with the Organization
            user: Required. Email address of a user
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/settings/azure/exemptions/{user}"
        params = {}
        try:
            result = await client.delete(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sync_exemptions_get_azure_exemptions(domain: str) -> str:
        """List of Sync Exemptions for an organization.

        API: GET /orgs/{domain}/settings/azure/exemptions

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/settings/azure/exemptions"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_sync_exemptions_put_azure_exemptions(domain: str, body: dict) -> str:
        """Add to organizations Sync Exemptions.

        API: PUT /orgs/{domain}/settings/azure/exemptions

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. List of comma separated emails to add to exemptions
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/settings/azure/exemptions"
        params = {}
        try:
            result = await client.put(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
