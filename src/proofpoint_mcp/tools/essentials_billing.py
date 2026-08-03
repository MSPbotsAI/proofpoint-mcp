import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_essentials_billing_get_billing_data(domain: str) -> str:
        """Read billing data for an Organization.

        API: GET /billing/{domain}

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/billing/{domain}"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_billing_get_billing_data_orgs(domain: str) -> str:
        """Read billing data for an Organization and its children.

        API: GET /billing/{domain}/orgs

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/billing/{domain}/orgs"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
