import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_essentials_domain_verification_get_domain_verification_code(domain: str, domaintobeverified: str) -> str:
        """Read the verification code required to verify the domain. Use this for TXT or META verification.

        API: GET /orgs/{domain}/domains/{domaintobeverified}/verification-code

        Args:
            domain: Required. Any Domain associated with the Organization
            domaintobeverified: Required. Name of the Domain to be verified
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains/{domaintobeverified}/verification-code"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_domain_verification_verify(domain: str, target_domain: str, method: str) -> str:
        """Run a verification check on the domain using the method specified. No Request data required, and result is shown via the HTTP response code. 204 = verified, 409 = not able to verify.

        API: PUT /orgs/{domain}/domains/{targetDomain}/verify/{method}

        Args:
            domain: Required. Any Domain associated with the Organization
            target_domain: Required. Name of the domain to act on
            method: Required. Which method to use
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/domains/{target_domain}/verify/{method}"
        params = {}
        try:
            result = await client.put(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
