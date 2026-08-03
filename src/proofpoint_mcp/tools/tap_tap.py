import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointTapClient, ProofpointError
from ._common import NO_TAP_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointTapClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_tap_tap_get_all_threats(since_seconds: str | None = None, since_time: str | None = None, interval: str | None = None, threat_status: str | None = None, format: str | None = None) -> str:
        """Get all threats (messages and clicks) from the TAP SIEM API for a given time window. Returns both delivered/blocked messages and permitted/blocked clicks. Live-verified: returns 401 (route recognized) with placeholder credentials against tap-api-v2.proofpoint.com.

        API: GET /v2/siem/all

        Args:
            since_seconds: Optional. Seconds ago to fetch threats from (max 3600). Mutually exclusive with sinceTime/interval.
            since_time: Optional. ISO 8601 date/time to fetch threats since. Mutually exclusive with sinceSeconds/interval.
            interval: Optional. Predefined interval PT30M or PT1H. Mutually exclusive with sinceSeconds/sinceTime.
            threat_status: Optional. Filter by threat status (active/cleared/falsePositive, default: active)
            format: Optional. Response format (json/syslog, default: json)
        """
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        params = {"sinceSeconds": since_seconds, "sinceTime": since_time, "interval": interval, "threatStatus": threat_status, "format": format}
        try:
            result = await client.get("/v2/siem/all", params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_tap_tap_get_clicks_blocked(since_seconds: str | None = None, since_time: str | None = None, interval: str | None = None, threat_status: str | None = None) -> str:
        """Get blocked clicks on threat URLs. Clicks that were prevented from reaching the malicious destination.

        API: GET /v2/siem/clicks/blocked

        Args:
            since_seconds: Optional. Seconds ago (max 3600)
            since_time: Optional. ISO 8601 date/time to fetch since
            interval: Optional. Predefined interval PT30M or PT1H
            threat_status: Optional. Filter by threat status
        """
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        params = {"sinceSeconds": since_seconds, "sinceTime": since_time, "interval": interval, "threatStatus": threat_status}
        try:
            result = await client.get("/v2/siem/clicks/blocked", params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_tap_tap_get_clicks_permitted(since_seconds: str | None = None, since_time: str | None = None, interval: str | None = None, threat_status: str | None = None) -> str:
        """Get permitted clicks on threat URLs. Clicks that were allowed through to the destination.

        API: GET /v2/siem/clicks/permitted

        Args:
            since_seconds: Optional. Seconds ago (max 3600)
            since_time: Optional. ISO 8601 date/time to fetch since
            interval: Optional. Predefined interval PT30M or PT1H
            threat_status: Optional. Filter by threat status
        """
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        params = {"sinceSeconds": since_seconds, "sinceTime": since_time, "interval": interval, "threatStatus": threat_status}
        try:
            result = await client.get("/v2/siem/clicks/permitted", params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_tap_tap_get_messages_blocked(since_seconds: str | None = None, since_time: str | None = None, interval: str | None = None, threat_status: str | None = None) -> str:
        """Get messages blocked that contained threats. Messages quarantined or rejected before reaching the recipient.

        API: GET /v2/siem/messages/blocked

        Args:
            since_seconds: Optional. Seconds ago (max 3600)
            since_time: Optional. ISO 8601 date/time to fetch since
            interval: Optional. Predefined interval PT30M or PT1H
            threat_status: Optional. Filter by threat status
        """
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        params = {"sinceSeconds": since_seconds, "sinceTime": since_time, "interval": interval, "threatStatus": threat_status}
        try:
            result = await client.get("/v2/siem/messages/blocked", params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_tap_tap_get_messages_delivered(since_seconds: str | None = None, since_time: str | None = None, interval: str | None = None, threat_status: str | None = None) -> str:
        """Get messages delivered containing threats. Messages that reached the recipient's mailbox despite containing identified threats.

        API: GET /v2/siem/messages/delivered

        Args:
            since_seconds: Optional. Seconds ago (max 3600)
            since_time: Optional. ISO 8601 date/time to fetch since
            interval: Optional. Predefined interval PT30M or PT1H
            threat_status: Optional. Filter by threat status
        """
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        params = {"sinceSeconds": since_seconds, "sinceTime": since_time, "interval": interval, "threatStatus": threat_status}
        try:
            result = await client.get("/v2/siem/messages/delivered", params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
