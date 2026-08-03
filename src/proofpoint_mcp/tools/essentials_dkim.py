import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_essentials_dkim_delete_all_for_domain(domain: str, target_domain: str) -> str:
        """Delete all DKIM keypairs associated with a domain.

        API: DELETE /orgs/{domain}/domains/{targetDomain}/dkim

        Args:
            domain: Required. Any Domain associated with the Organization
            target_domain: Required. Name of the domain to act on
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains/{target_domain}/dkim"
        params = {}
        try:
            result = await client.delete(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_dkim_delete_by_selector(domain: str, target_domain: str, selector: str) -> str:
        """Delete a DKIM keypair by selector name.

        API: DELETE /orgs/{domain}/domains/{targetDomain}/dkim/{selector}

        Args:
            domain: Required. Any Domain associated with the Organization
            target_domain: Required. Name of the domain to act on
            selector: Required. DKIM configuration name
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains/{target_domain}/dkim/{selector}"
        params = {}
        try:
            result = await client.delete(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_dkim_get_all_dkim_for_domain(domain: str, target_domain: str) -> str:
        """Read DKIM Signing data for all keypairs associated with this domain.

        API: GET /orgs/{domain}/domains/{targetDomain}/dkim

        Args:
            domain: Required. Any Domain associated with the Organization
            target_domain: Required. Name of the domain to act on
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains/{target_domain}/dkim"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_dkim_get_by_selector(domain: str, target_domain: str, selector: str) -> str:
        """Read DKIM Signing data for a single keypair by selector name.

        API: GET /orgs/{domain}/domains/{targetDomain}/dkim/{selector}

        Args:
            domain: Required. Any Domain associated with the Organization
            target_domain: Required. Name of the domain to act on
            selector: Required. DKIM configuration name
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains/{target_domain}/dkim/{selector}"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_dkim_post(domain: str, target_domain: str, selector: str, body: dict) -> str:
        """Create a DKIM keypair.

        API: POST /orgs/{domain}/domains/{targetDomain}/dkim/{selector}

        Args:
            domain: Required. Any Domain associated with the Organization
            target_domain: Required. Name of the domain to act on
            selector: Required. DKIM configuration name
            body: Required. DKIM Post data
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains/{target_domain}/dkim/{selector}"
        params = {}
        try:
            result = await client.post(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_dkim_verify_dkim(domain: str, target_domain: str, selector: str) -> str:
        """Verify the DKIM keypair is valid by verifying the Public Key in DNS.

        API: PUT /orgs/{domain}/domains/{targetDomain}/dkim/{selector}/verify

        Args:
            domain: Required. Any Domain associated with the Organization
            target_domain: Required. Name of the domain to act on
            selector: Required. DKIM configuration name
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains/{target_domain}/dkim/{selector}/verify"
        params = {}
        try:
            result = await client.put(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
