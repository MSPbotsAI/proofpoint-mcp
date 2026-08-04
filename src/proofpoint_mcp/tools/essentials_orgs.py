import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:
    @mcp.tool()
    async def proofpoint_essentials_orgs_get_org(domain: str) -> str:
        """Read an Organization.

        API: GET /orgs/{domain}

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_orgs_patch_org(domain: str, body: dict) -> str:
        """Update an Organization.

        API: PATCH /orgs/{domain}

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. one or more supported fields may be individually updated
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}"
        params = {}
        try:
            result = await client.patch(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_orgs_post_org(domain: str, body: dict) -> str:
        """Create a new Organization. Batch POST supported with list of Organization objects.

        API: POST /orgs/{domain}/orgs

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. Domain data
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/orgs"
        params = {}
        try:
            result = await client.post(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
