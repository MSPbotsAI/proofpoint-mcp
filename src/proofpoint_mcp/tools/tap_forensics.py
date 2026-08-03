import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointTapClient, ProofpointError
from ._common import NO_TAP_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointTapClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_tap_forensics_get_forensics(threat_id: str | None = None, campaign_id: str | None = None, include_campaign_forensics: str | None = None) -> str:
        """Fetch forensic evidence for a specific threat or campaign — behavioral analysis, network activity, file modifications, and other indicators. Exactly one of threat_id or campaign_id must be supplied (mutually exclusive, per official Forensics API doc). Live-verified: the query-param path shape (/v2/forensics?threatId=...) returns 401; the open-source project's original path-segment shape (/v2/forensics/threat/{id}) does not exist (404) and was corrected here.

        API: GET /v2/forensics

        Args:
            threat_id: Optional. Threat ID to fetch forensics for — mutually exclusive with campaignId, exactly one is required
            campaign_id: Optional. Campaign ID to fetch aggregate forensics for — mutually exclusive with threatId, exactly one is required
            include_campaign_forensics: Optional. Only usable with threatId. If true and the threat is associated with a campaign, returns aggregate forensics for the whole campaign instead of just this threat (default: false)
        """
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        params = {"threatId": threat_id, "campaignId": campaign_id, "includeCampaignForensics": include_campaign_forensics}
        try:
            result = await client.get("/v2/forensics", params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
