import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:
    @mcp.tool()
    async def proofpoint_essentials_domains_get_domain(domain: str, target_domain: str) -> str:
        """Read a single Domain associated with an Organization.

        API: GET /orgs/{domain}/domains/{targetDomain}

        Args:
            domain: Required. Any Domain associated with the Organization
            target_domain: Required. Name of the Domain to be retrieved
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains/{target_domain}"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_domains_get_domains(domain: str) -> str:
        """Read all domains associated with an Organization.

        API: GET /orgs/{domain}/domains

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_domains_post_domain(domain: str, body: dict) -> str:
        """Create a new Domain. Batch POST supported with list of Domain objects.

        API: POST /orgs/{domain}/domains

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. Domain data
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains"
        params = {}
        try:
            result = await client.post(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

