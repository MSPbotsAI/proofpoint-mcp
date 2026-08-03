import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_essentials_authentication_delete_idp(domain: str, uuid: str) -> str:
        """Delete an Identity Provider (IDP).

        API: DELETE /orgs/{domain}/authentication/settings/idps/{uuid}

        Args:
            domain: Required. Any Domain associated with the Organization
            uuid: Required. UUID of the IDP to delete
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/authentication/settings/idps/{uuid}"
        params = {}
        try:
            result = await client.delete(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_authentication_get_all_idps(domain: str) -> str:
        """Read a list of all Identity Providers (IDPs) for the target Organization.

        API: GET /orgs/{domain}/authentication/settings/idps

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/authentication/settings/idps"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_authentication_get_idp_by_uuid(domain: str, uuid: str) -> str:
        """Read a single Identity Provider (IDP).

        API: GET /orgs/{domain}/authentication/settings/idps/{uuid}

        Args:
            domain: Required. Any Domain associated with the Organization
            uuid: Required. UUID of the IDP to fetch
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/authentication/settings/idps/{uuid}"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_authentication_get_login_settings(domain: str) -> str:
        """Read Authentication login settings for the target Organization.

        API: GET /orgs/{domain}/authentication/settings/login

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/authentication/settings/login"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_authentication_get_mfa_settings(domain: str) -> str:
        """Read MFA settings for the target Organization.

        API: GET /orgs/{domain}/authentication/settings/mfa

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/authentication/settings/mfa"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_authentication_post_idp(domain: str, body: dict) -> str:
        """Create a new Identity Provider (IDP).

        API: POST /orgs/{domain}/authentication/settings/idps

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. IDP details
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/authentication/settings/idps"
        params = {}
        try:
            result = await client.post(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_authentication_put_idp(domain: str, uuid: str, body: dict) -> str:
        """Update an Identity Provider (IDP).

        API: PUT /orgs/{domain}/authentication/settings/idps/{uuid}

        Args:
            domain: Required. Any Domain associated with the Organization
            uuid: Required. UUID of the IDP to update
            body: Required. IDP settings to update
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/authentication/settings/idps/{uuid}"
        params = {}
        try:
            result = await client.put(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_authentication_put_login_settings(domain: str, body: dict) -> str:
        """Update Login settings for the target Organization.

        API: PUT /orgs/{domain}/authentication/settings/login

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. Authentication login settings to update
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/authentication/settings/login"
        params = {}
        try:
            result = await client.put(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_authentication_put_mfa_settings(domain: str, body: dict) -> str:
        """Update MFA settings for the target Organization.

        API: PUT /orgs/{domain}/authentication/settings/mfa

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. Authentication login settings to update
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/authentication/settings/mfa"
        params = {}
        try:
            result = await client.put(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
