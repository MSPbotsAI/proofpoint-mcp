import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointTapClient, ProofpointError
from ._common import NO_TAP_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointTapClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_tap_campaign_get_campaign(campaign_id: str) -> str:
        """Fetch detailed information for a given campaign: description, actors, malware families, techniques, and threat variants. Live-verified: returns 401 (route recognized) with a placeholder campaign id and credentials.

        API: GET /v2/campaign/{campaign_id}

        Args:
            campaign_id: Required. The campaign ID to look up (usually found in SIEM API events)
        """
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        path = f"/v2/campaign/{campaign_id}"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_tap_campaign_list_ids(interval: str, size: str | None = None, page: str | None = None) -> str:
        """Fetch a list of IDs of campaigns active in a time window, sorted by last-updated timestamp.

        API: GET /v2/campaign/ids

        Args:
            interval: Required. ISO8601-formatted interval (min 30 seconds, max 1 day), e.g. 2020-05-01T12:00:00Z/2020-05-01T13:00:00Z or PT30M/2020-05-01T12:30:00Z
            size: Optional. Max campaign IDs to return (default: 100, max: 200)
            page: Optional. Page of results, in multiples of size (default: 1)
        """
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        params = {"interval": interval, "size": size, "page": page}
        try:
            result = await client.get("/v2/campaign/ids", params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
