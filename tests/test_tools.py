"""tools/list snapshot + error-envelope mapping tests.

No network calls: tool enumeration goes through FastMCP's in-process
list_tools(), and the error-code mapping is tested directly against
ProofpointError, independent of any real HTTP request.
"""

import pytest

from proofpoint_mcp.api_client import ProofpointError
from proofpoint_mcp.config import Settings
from proofpoint_mcp.server import create_mcp_server

# name -> (required params, expected annotation flags)
EXPECTED_TOOLS = {
    "proofpoint_tap_people_get_vap": ({"window"}, {"readOnlyHint": True}),
    "proofpoint_tap_tap_get_all_threats": (set(), {"readOnlyHint": True}),
    "proofpoint_tap_url_defense_decode": ({"body"}, {"readOnlyHint": True}),
    "proofpoint_essentials_domains_get_domain": (
        {"domain", "target_domain"},
        {"readOnlyHint": True},
    ),
    "proofpoint_essentials_domains_get_domains": ({"domain"}, {"readOnlyHint": True}),
    "proofpoint_essentials_domains_post_domain": (
        {"domain", "body"},
        {"readOnlyHint": False, "idempotentHint": False},
    ),
    "proofpoint_essentials_me_get_me": (set(), {"readOnlyHint": True}),
    "proofpoint_essentials_orgs_get_org": ({"domain"}, {"readOnlyHint": True}),
    "proofpoint_essentials_orgs_patch_org": (
        {"domain", "body"},
        {"readOnlyHint": False, "idempotentHint": True},
    ),
    "proofpoint_essentials_orgs_post_org": (
        {"domain", "body"},
        {"readOnlyHint": False, "idempotentHint": False},
    ),
    "proofpoint_essentials_users_delete_user": (
        {"domain", "user"},
        {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True},
    ),
    "proofpoint_essentials_users_get_user": ({"domain", "user"}, {"readOnlyHint": True}),
    "proofpoint_essentials_users_get_users": ({"domain"}, {"readOnlyHint": True}),
    "proofpoint_essentials_users_post_user": (
        {"domain", "body"},
        {"readOnlyHint": False, "idempotentHint": False},
    ),
    "proofpoint_essentials_users_put_user": (
        {"domain", "user", "body"},
        {"readOnlyHint": False, "idempotentHint": True},
    ),
}


@pytest.mark.asyncio
async def test_tools_list_snapshot():
    mcp = create_mcp_server(Settings())
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert names == set(EXPECTED_TOOLS), f"unexpected tool set: {names}"

    by_name = {t.name: t for t in tools}
    for name, (expected_required, expected_flags) in EXPECTED_TOOLS.items():
        tool = by_name[name]
        required = set(tool.inputSchema.get("required", []))
        assert required == expected_required, f"{name}: required={required}"

        assert tool.annotations is not None, f"{name}: missing annotations"
        for flag, expected_value in expected_flags.items():
            actual = getattr(tool.annotations, flag)
            assert actual is expected_value, f"{name}.{flag}={actual}, want {expected_value}"

        description = tool.description or ""
        assert len(description) <= 500, f"{name}: description too long ({len(description)})"
        first_line = description.strip().splitlines()[0]
        assert len(first_line) <= 100, f"{name}: first line too long: {first_line!r}"
        assert "API:" not in description, f"{name}: description leaks implementation detail"


@pytest.mark.asyncio
async def test_tools_count_within_sop_budget():
    mcp = create_mcp_server(Settings())
    tools = await mcp.list_tools()
    assert len(tools) == 15
    assert len(tools) <= 20


@pytest.mark.asyncio
async def test_service_instructions_present_and_bounded():
    mcp = create_mcp_server(Settings())
    assert mcp.instructions
    assert len(mcp.instructions) <= 1500


@pytest.mark.parametrize(
    "status_code,expected_code,expected_retryable",
    [
        (0, "upstream_error", True),
        (400, "invalid_argument", False),
        (401, "unauthorized", False),
        (403, "unauthorized", False),
        (404, "not_found", False),
        (422, "invalid_argument", False),
        (429, "rate_limited", True),
        (500, "upstream_error", True),
        (503, "upstream_error", True),
    ],
)
def test_error_envelope_mapping(status_code, expected_code, expected_retryable):
    import json

    err = ProofpointError(status_code, "boom")
    envelope = json.loads(err.to_envelope())
    assert envelope["error"]["code"] == expected_code
    assert envelope["error"]["retryable"] is expected_retryable
    assert envelope["error"]["message"] == "boom"
