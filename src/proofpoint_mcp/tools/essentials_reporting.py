import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_essentials_reporting_get_reporting_period(domain: str, period: str) -> str:
        """Read statistics data for an Organization.

        API: GET /reporting/{domain}/{period}

        Args:
            domain: Required. Any Domain associated with the Organization
            period: Required. Time range for the report
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/reporting/{domain}/{period}"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_reporting_get_reporting_period_by_direction(domain: str, period: str, direction: str) -> str:
        """Read statistics data for an Organization.

        API: GET /reporting/{domain}/{period}/{direction}

        Args:
            domain: Required. Any Domain associated with the Organization
            period: Required. Time range for the report
            direction: Required. Mailflow direction: Choice of inbound/outbound
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/reporting/{domain}/{period}/{direction}"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
