import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ProofpointEssentialsClient, ProofpointError
from ._common import NO_ESSENTIALS_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ProofpointEssentialsClient | None]) -> None:

    @mcp.tool()
    async def proofpoint_essentials_products_get_one(domain: str, label: str) -> str:
        """Read a single Product by Label.

        API: GET /orgs/{domain}/products/{label}

        Args:
            domain: Required. Any Domain associated with the Organization
            label: Required. Product identifier
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/products/{label}"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_products_get_products(domain: str) -> str:
        """Read a list of Products applicable to an Organization. Includes both available and purchased products.

        API: GET /orgs/{domain}/products

        Args:
            domain: Required. Any Domain associated with the Organization
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/products"
        params = {}
        try:
            result = await client.get(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_products_product_delete(domain: str, label: str) -> str:
        """Delete a Product subscription. NOTE this will not normally be available to customers depending on the Product.

        API: DELETE /orgs/{domain}/products/{label}

        Args:
            domain: Required. Any Domain associated with the Organization
            label: Required. Product identifier
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/products/{label}"
        params = {}
        try:
            result = await client.delete(path, params=params)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_products_product_patch(domain: str, label: str, body: dict) -> str:
        """Update a Product.

        API: PATCH /orgs/{domain}/products/{label}

        Args:
            domain: Required. Any Domain associated with the Organization
            label: Required. Product identifier
            body: Required. Product data (all fields optional)
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/products/{label}"
        params = {}
        try:
            result = await client.patch(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def proofpoint_essentials_products_products_post(domain: str, body: dict) -> str:
        """Used to purchase a Product.

        API: POST /orgs/{domain}/products

        Args:
            domain: Required. Any Domain associated with the Organization
            body: Required. Product Post data
        """
        client = client_factory()
        if client is None:
            return NO_ESSENTIALS_TOKEN
        path = f"/orgs/{domain}/products"
        params = {}
        try:
            result = await client.post(path, params=params, json_body=body)
            return json.dumps(result, indent=2, default=str)
        except ProofpointError as e:
            return f"Error: {e}"
