import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_essentials_stats_partner_stats_all_orgs(domain: str, period: str | None = None, page: str | None = None, page_size: str | None = None) -> str:
        """Read statistics data for an Organization and its children for the last 1/7/30/90 days.

        API: GET /stats/{domain}/partner/orgs

        Args:
            domain: Required. Any Domain associated with the Organization
            period: Optional. The response data may be filtered by period interval. Example shown is for '90d'.
            page: Optional. Data may be 'paged'. Specify a page number to retrieve the desired set of results.
            page_size: Optional. Data may be 'paged'. Specify a page size to retrieve the desired number of results per page. Max: 50000. The default is intentionally large to allow most partners to retrieve all data in a single request.
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/stats/{domain}/partner/orgs"
        params = {"period": period, "page": page, "page_size": page_size}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_stats_partner_stats_single_org(domain: str, period: str | None = None, page: str | None = None, page_size: str | None = None) -> str:
        """Read statistics data for an Organization for the last 1/7/30/90 days.

        API: GET /stats/{domain}/partner

        Args:
            domain: Required. Any Domain associated with the Organization
            period: Optional. The response data may be filtered by period interval. Example shown is for '90d'.
            page: Optional. Data may be 'paged'. Specify a page number to retrieve the desired set of results.
            page_size: Optional. Data may be 'paged'. Specify a page size to retrieve the desired number of results per page. Max: 50000. The default is intentionally large to allow most partners to retrieve all data in a single request.
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/stats/{domain}/partner"
        params = {"period": period, "page": page, "page_size": page_size}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
