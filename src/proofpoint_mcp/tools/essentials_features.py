import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_essentials_features_get_features(domain: str) -> str:
        """Read all Features relevant to an Organization. Note that the items returned will be specific to the licensing package.

        API: GET /orgs/{domain}/features

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/features"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_features_put_features(domain: str, body: dict) -> str:
        """Update an Organization's feature set. The feature set will differ for different types of licensing package so the applicable features should be obtained by a GET first, then updated as appropriate.

        API: PUT /orgs/{domain}/features

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. Feature data
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/features"
        params = {}
        try:
            result = await client.put(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
