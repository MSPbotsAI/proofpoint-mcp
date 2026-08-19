from collections.abc import Callable
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .._json import dump_json_capped
from ..api_client import ProofpointError, ProofpointTapClient
from ._common import NO_TAP_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointTapClient | None]) -> None:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def proofpoint_tap_tap_get_all_threats(
        since_seconds: Annotated[
            str | None,
            Field(description="Seconds ago to fetch threats from, max 3600. Mutually exclusive with since_time/interval."),
        ] = None,
        since_time: Annotated[
            str | None,
            Field(description="ISO 8601 date/time to fetch threats since. Mutually exclusive with since_seconds/interval."),
        ] = None,
        interval: Annotated[
            str | None,
            Field(description='Predefined interval, "PT30M" or "PT1H". Mutually exclusive with since_seconds/since_time.'),
        ] = None,
        threat_status: Annotated[
            str | None,
            Field(description='Filter by status: "active", "cleared", or "falsePositive". Default "active".'),
        ] = None,
        format: Annotated[
            str | None, Field(description='Response format, "json" or "syslog". Default "json".')
        ] = None,
    ) -> str:
        """List delivered/blocked messages and permitted/blocked clicks from TAP SIEM.

        Covers a single time window; provide at most one of since_seconds,
        since_time, or interval.
        """
        client = client_factory()
        if client is None:
            return NO_TAP_TOKEN
        params = {
            "sinceSeconds": since_seconds,
            "sinceTime": since_time,
            "interval": interval,
            "threatStatus": threat_status,
            "format": format,
        }
        try:
            result = await client.get("/v2/siem/all", params=params)
            return dump_json_capped(result)
        except ProofpointError as e:
            return e.to_envelope()
