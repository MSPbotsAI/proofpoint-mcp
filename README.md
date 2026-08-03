# proofpoint-mcp

MCP server for **Proofpoint** — wraps two distinct Proofpoint products/APIs behind one MCP server: **TAP (Targeted Attack Protection)**, threat/campaign/people-risk intelligence, and **Essentials**, the Proofpoint Essentials tenant/user/domain administration API.

## Overview

- Stateless HTTP service. No credentials are ever persisted — each request supplies its own credentials via headers, used only for the lifetime of that single request.
- Supports concurrent requests; per-request credential isolation is done via two independent Python `contextvars` (one per product), not a global/shared client instance.
- Entry points: `POST /mcp` (MCP protocol) and `GET /health` (health check).
- Default port: `8080` (configurable via `MCP_HTTP_PORT`).
- **This server wraps two genuinely separate Proofpoint products with two separate credential types.** A caller using only one product's tools does not need to also supply the other product's credentials — see Authentication below.

## Scope

**89 tools**: 12 for TAP, 77 for Proofpoint Essentials.

No official Proofpoint MCP server exists (confirmed by searching both the `wyre-technology` and `MSPbotsAI` GitHub orgs, and Proofpoint's own docs/marketplace). A community project, [`wyre-technology/proofpoint-mcp`](https://github.com/wyre-technology/proofpoint-mcp), exists and claims TAP + "Essentials" coverage, but its actual code only ever calls the TAP host (`tap-api-v2.proofpoint.com`) — it has no Essentials API integration at all despite the README's claim. This server is a from-scratch build, not a fork, and additionally covers the full Essentials API the community project does not.

- **Essentials (77 tools)**: generated directly from Proofpoint's own official OpenAPI 3.0 spec, downloaded from `https://us1.proofpointessentials.com/apidocs/apidocs/docs`. Full CRUD across Organizations, Domains, Users, DKIM, Authentication (IdP/MFA/login settings), Sender Lists, Sync Exemptions, Billing, Licensing, and more — this fully covers the task's stated need (tenant/user account creation and synchronization).
- **TAP (12 tools)**: hand-built from Proofpoint's official Threat Insight Dashboard API documentation (`help.proofpoint.com`) plus live endpoint verification, **not** ported as-is from the community repo. See **Verification Methodology** below for why this is a much smaller set than the community repo's 38 TAP tools.

## Verification Methodology (why TAP is 12 tools, not 38)

The community repo's TAP module defines 38 tools across 11 categories (`dlp`, `events`, `forensics`, `people`, `policy`, `quarantine`, `reports`, `smart_search`, `tap`, `threat_intel`, `url_defense`). Per explicit user instruction to drop anything unconfirmed and defer to the official API documentation, every category was independently checked two ways:

1. **Live HTTP status-code testing** against `https://tap-api-v2.proofpoint.com` with intentionally invalid (`fake:fake`) credentials. A `401 Unauthorized` with a Proofpoint auth-failure message means the route is recognized by the server (only credentials were rejected); a `404 Not Found` means the route does not exist at that path at all.
2. **Cross-referencing against Proofpoint's official docs** at `help.proofpoint.com` for each of the 8 documented TAP sub-APIs (Campaign, Forensics, People, Reports, SIEM, Supplier Threat Protection, Threats, URL Decoder).

Results:

| Community repo category | Verdict | Disposition |
|---|---|---|
| `tap` (SIEM: all/messages/clicks) | **Real**, matches official SIEM API doc exactly | Kept as-is (5 tools) |
| `people.get_vap`, `people.get_top_clickers` | Real, but `window` was wrongly optional — official People API doc requires it | Kept, `window` now required |
| `people.get_user_risk` | **Fake** — no such endpoint in official docs or live host | Removed |
| `threat_intel.get_campaign` (`/v2/campaign/{id}`) | Real | Kept, moved to `campaign` category |
| `threat_intel.list_families` | **Fake** — 404 live, not in official Campaign API doc | Removed |
| `threat_intel.get_iocs` | Unconfirmed — path shape only inferred from the repo's own conditional logic, not documented anywhere | Removed |
| — (missing) | Official Campaign API doc documents a second endpoint, `GET /v2/campaign/ids`, that the community repo never implemented | **Added** as `campaign.list_ids` |
| `forensics.get_threat`, `get_campaign`, `search_messages`, `pull_messages` (path-segment style, `/v2/forensics/threat/{id}`, `/v1/trap/search`, `/v1/trap/pull`) | **Wrong path shape** — 404 live; official Forensics API doc specifies a single `GET /v2/forensics?threatId=X\|campaignId=X` endpoint with mutually-exclusive query params | Replaced all 4 with 1 corrected tool, `forensics.get_forensics` |
| `threat_intel.get_by_id` (`/v2/threat/summary/{id}`) | Real (401 live). Official "Threats API" doc page is login-gated (`help.proofpoint.com` returned "You do not have permission to view this page") so its full schema could not be independently reviewed beyond this live-verified endpoint | Kept, moved to `threats` category, documented as partially-unverifiable |
| `url_defense.decode` (`POST /v2/url/decode`) | Real, matches official URL Decoder API doc exactly (the doc confirms this is the *only* endpoint in that sub-API) | Kept |
| `url_defense.analyze` | **Fake** — no such endpoint; official docs confirm URL Decoder API has exactly one operation | Removed |
| `dlp` (3 tools), `policy` (3), `quarantine` (4), `smart_search` (3) | **Entirely fake** — all 404 live; none of these categories exist anywhere in Proofpoint's official TAP docs. The community repo's own source comments cite `help.proofpoint.com/Proofpoint_Essentials/.../Administrator_Topics/...` doc paths (Essentials *UI* features), but the code sends requests to the TAP host regardless, and none of them appear in the real Essentials OpenAPI spec either. Most likely fabricated/guessed without live-account verification. | Removed entirely (13 tools) |
| `reports` (4 tools, e.g. `org_summary`) | **Fake at these paths.** While investigating, discovered Proofpoint does have a real "Reports"/"Dash Reports" API — but it's a **completely separate product**: different host (`threatprotection-api.proofpoint.com`), different auth (OAuth2 `client_credentials` via `POST https://auth.proofpoint.com/v1/token`), different paths (`/executive-summary/...`, `/effectiveness-reports/...`, etc.). None of the community repo's `/v1/reports/*` paths match this real product. | Removed; documented as a known gap (see below), not built |
| `events` (3 tools) | `list` coincidentally reused the real `/v2/siem/all` route (401), but `get_details`/`get_stats` are fake (404), and the whole category duplicates the `tap` category's SIEM coverage under a different (partially wrong) shape | Removed entirely; SIEM coverage is fully provided by the `tap` category |

**Net result**: 12 TAP tools, every one of which returns `401` (route recognized, credentials rejected) when live-tested against `https://tap-api-v2.proofpoint.com` with placeholder credentials — no tool in this server points at a nonexistent or fabricated endpoint.

## Authentication

Two independent credential sets, one per wrapped product. Supply whichever set matches the tools you intend to call; a request is only rejected outright if **neither** set is present.

### HEADER 授权参数说明

| Header | 类型 | 是否必填 | 默认值 | 枚举值 | 字段描述 | Example |
|---|---|---|---|---|---|---|
| `X-Proofpoint-Tap-Service-Principal` | string | 二选一(TAP) | 无 | 无 | TAP API Service Principal（在 Threat Insight Dashboard → Settings → Connected Applications → Service Credentials 中生成），随 `X-Proofpoint-Tap-Service-Secret` 一起转发为上游 HTTP Basic Auth | `X-Proofpoint-Tap-Service-Principal: abc123-...` |
| `X-Proofpoint-Tap-Service-Secret` | string | 二选一(TAP) | 无 | 无 | TAP API Service Secret，与上面的 Service Principal 配对使用 | `X-Proofpoint-Tap-Service-Secret: xxxxxxxx` |
| `X-Proofpoint-Tap-Base-Url` | string | 否 | `https://tap-api-v2.proofpoint.com` | 无 | 覆盖默认 TAP API host（一般无需设置） | `X-Proofpoint-Tap-Base-Url: https://tap-api-v2.proofpoint.com` |
| `X-Proofpoint-Essentials-Username` | string | 二选一(Essentials) | 无 | 无 | Proofpoint Essentials API 用户名，随 Password 一起转发为上游 `X-User` 请求头 | `X-Proofpoint-Essentials-Username: api-user@example.com` |
| `X-Proofpoint-Essentials-Password` | string | 二选一(Essentials) | 无 | 无 | Proofpoint Essentials API 密码，转发为上游 `X-Password` 请求头 | `X-Proofpoint-Essentials-Password: xxxxxxxx` |
| `X-Proofpoint-Essentials-Base-Url` | string | 二选一(Essentials) | 无 | 无 | 租户专属的 Essentials API host（每个租户不同，例如 `us1.proofpointessentials.com`），Essentials 凭据必须同时提供此项 | `X-Proofpoint-Essentials-Base-Url: us1.proofpointessentials.com` |

Missing both credential sets returns `401`:
```json
{
  "error": "Missing credentials",
  "message": "This server requires either the TAP credential set (X-Proofpoint-Tap-Service-Principal + X-Proofpoint-Tap-Service-Secret) or the Essentials credential set (X-Proofpoint-Essentials-Username + X-Proofpoint-Essentials-Password + X-Proofpoint-Essentials-Base-Url) — at least one is required",
  "required_headers": [
    "X-Proofpoint-Tap-Service-Principal + X-Proofpoint-Tap-Service-Secret",
    "OR X-Proofpoint-Essentials-Username + X-Proofpoint-Essentials-Password + X-Proofpoint-Essentials-Base-Url"
  ],
  "optional_headers": ["X-Proofpoint-Tap-Base-Url"]
}
```

Calling a TAP tool without TAP credentials (even if Essentials credentials were supplied), or vice versa, does not error at the transport level — it returns that tool's own `NO_TAP_TOKEN` / `NO_ESSENTIALS_TOKEN` string result instead.

## Environment Variables

| Variable | 类型 | 是否必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `MCP_HTTP_PORT` | int | 否 | `8080` | HTTP 监听端口 |
| `MCP_HTTP_HOST` | string | 否 | `0.0.0.0` | HTTP 监听地址 |
| `PROOFPOINT_TAP_BASE_URL` | string | 否 | `https://tap-api-v2.proofpoint.com` | TAP API 默认 host（可被请求头覆盖） |

## MCP Endpoint

- `POST /mcp` — MCP protocol (streamable HTTP transport)
- `GET /health` — health check, returns `{"status": "ok", "service": "proofpoint-mcp", "transport": "http"}`

## Tool List

Tool names are `proofpoint_<product>_<category>_<operation>`. Essentials tool signatures/params were generated directly from Proofpoint's own OpenAPI spec (`domain` is the Essentials org identifier path parameter used throughout, per that spec's own convention — not a DNS domain in most calls). `body` parameters for create/update/patch endpoints are accepted as a generic `dict` matching the corresponding OpenAPI request schema.

| Category | Tool | Method + Path | Params |
|---|---|---|---|
| essentials/authentication | `proofpoint_essentials_authentication_delete_idp` | DELETE /orgs/{domain}/authentication/settings/idps/{uuid} | domain(required), uuid(required) |
| essentials/authentication | `proofpoint_essentials_authentication_get_all_idps` | GET /orgs/{domain}/authentication/settings/idps | domain(required) |
| essentials/authentication | `proofpoint_essentials_authentication_get_idp_by_uuid` | GET /orgs/{domain}/authentication/settings/idps/{uuid} | domain(required), uuid(required) |
| essentials/authentication | `proofpoint_essentials_authentication_get_login_settings` | GET /orgs/{domain}/authentication/settings/login | domain(required) |
| essentials/authentication | `proofpoint_essentials_authentication_get_mfa_settings` | GET /orgs/{domain}/authentication/settings/mfa | domain(required) |
| essentials/authentication | `proofpoint_essentials_authentication_post_idp` | POST /orgs/{domain}/authentication/settings/idps | domain(required), body(required) |
| essentials/authentication | `proofpoint_essentials_authentication_put_idp` | PUT /orgs/{domain}/authentication/settings/idps/{uuid} | domain(required), uuid(required), body(required) |
| essentials/authentication | `proofpoint_essentials_authentication_put_login_settings` | PUT /orgs/{domain}/authentication/settings/login | domain(required), body(required) |
| essentials/authentication | `proofpoint_essentials_authentication_put_mfa_settings` | PUT /orgs/{domain}/authentication/settings/mfa | domain(required), body(required) |
| essentials/billing | `proofpoint_essentials_billing_get_billing_data` | GET /billing/{domain} | domain(required) |
| essentials/billing | `proofpoint_essentials_billing_get_billing_data_orgs` | GET /billing/{domain}/orgs | domain(required) |
| essentials/dkim | `proofpoint_essentials_dkim_delete_all_for_domain` | DELETE /orgs/{domain}/domains/{targetDomain}/dkim | domain(required), target_domain(required) |
| essentials/dkim | `proofpoint_essentials_dkim_delete_by_selector` | DELETE /orgs/{domain}/domains/{targetDomain}/dkim/{selector} | domain(required), target_domain(required), selector(required) |
| essentials/dkim | `proofpoint_essentials_dkim_get_all_dkim_for_domain` | GET /orgs/{domain}/domains/{targetDomain}/dkim | domain(required), target_domain(required) |
| essentials/dkim | `proofpoint_essentials_dkim_get_by_selector` | GET /orgs/{domain}/domains/{targetDomain}/dkim/{selector} | domain(required), target_domain(required), selector(required) |
| essentials/dkim | `proofpoint_essentials_dkim_post` | POST /orgs/{domain}/domains/{targetDomain}/dkim/{selector} | domain(required), target_domain(required), selector(required), body(required) |
| essentials/dkim | `proofpoint_essentials_dkim_verify_dkim` | PUT /orgs/{domain}/domains/{targetDomain}/dkim/{selector}/verify | domain(required), target_domain(required), selector(required) |
| essentials/domain verification | `proofpoint_essentials_domain_verification_get_domain_verification_code` | GET /orgs/{domain}/domains/{domaintobeverified}/verification-code | domain(required), domaintobeverified(required) |
| essentials/domain verification | `proofpoint_essentials_domain_verification_verify` | PUT /orgs/{domain}/domains/{targetDomain}/verify/{method} | domain(required), target_domain(required), method(required) |
| essentials/domains | `proofpoint_essentials_domains_delete_domain` | DELETE /orgs/{domain}/domains/{targetDomain} | domain(required), target_domain(required) |
| essentials/domains | `proofpoint_essentials_domains_get_domain` | GET /orgs/{domain}/domains/{targetDomain} | domain(required), target_domain(required) |
| essentials/domains | `proofpoint_essentials_domains_get_domains` | GET /orgs/{domain}/domains | domain(required) |
| essentials/domains | `proofpoint_essentials_domains_get_health` | GET /orgs/{domain}/domains/{domaintobediagnosed}/health | domain(required), domaintobediagnosed(required) |
| essentials/domains | `proofpoint_essentials_domains_post_domain` | POST /orgs/{domain}/domains | domain(required), body(required) |
| essentials/domains | `proofpoint_essentials_domains_put_domain` | PUT /orgs/{domain}/domains/{targetDomain} | domain(required), target_domain(required), body(required) |
| essentials/email tagging | `proofpoint_essentials_email_tagging_delete_email_tagging_exemptions` | DELETE /orgs/{domain}/email-tagging/exemptions | domain(required) |
| essentials/email tagging | `proofpoint_essentials_email_tagging_get` | GET /orgs/{domain}/email-tagging | domain(required) |
| essentials/email tagging | `proofpoint_essentials_email_tagging_get_email_tagging_exemptions` | GET /orgs/{domain}/email-tagging/exemptions | domain(required) |
| essentials/email tagging | `proofpoint_essentials_email_tagging_patch` | PATCH /orgs/{domain}/email-tagging | domain(required), body(required) |
| essentials/email tagging | `proofpoint_essentials_email_tagging_post_email_tagging_exemptions` | POST /orgs/{domain}/email-tagging/exemptions | domain(required), body(required) |
| essentials/email tagging | `proofpoint_essentials_email_tagging_put` | PUT /orgs/{domain}/email-tagging | domain(required), body(required) |
| essentials/endpoints | `proofpoint_essentials_endpoints_get_endpoints` | GET /endpoints/{domaintobechecked} | domaintobechecked(required) |
| essentials/features | `proofpoint_essentials_features_get_features` | GET /orgs/{domain}/features | domain(required) |
| essentials/features | `proofpoint_essentials_features_put_features` | PUT /orgs/{domain}/features | domain(required), body(required) |
| essentials/licensing | `proofpoint_essentials_licensing_get_licensing` | GET /orgs/{domain}/licensing | domain(required) |
| essentials/licensing | `proofpoint_essentials_licensing_put_licensing` | PUT /orgs/{domain}/licensing | domain(required) |
| essentials/me | `proofpoint_essentials_me_get_me` | GET /me | none |
| essentials/orgs | `proofpoint_essentials_orgs_delete_org` | DELETE /orgs/{domain} | domain(required) |
| essentials/orgs | `proofpoint_essentials_orgs_get_child_orgs` | GET /orgs/{domain}/orgs | domain(required) |
| essentials/orgs | `proofpoint_essentials_orgs_get_org` | GET /orgs/{domain} | domain(required) |
| essentials/orgs | `proofpoint_essentials_orgs_patch_org` | PATCH /orgs/{domain} | domain(required), body(required) |
| essentials/orgs | `proofpoint_essentials_orgs_post_org` | POST /orgs/{domain}/orgs | domain(required), body(required) |
| essentials/package | `proofpoint_essentials_package_put_package` | PUT /orgs/{domain}/package | domain(required), body(required) |
| essentials/products | `proofpoint_essentials_products_get_one` | GET /orgs/{domain}/products/{label} | domain(required), label(required) |
| essentials/products | `proofpoint_essentials_products_get_products` | GET /orgs/{domain}/products | domain(required) |
| essentials/products | `proofpoint_essentials_products_product_delete` | DELETE /orgs/{domain}/products/{label} | domain(required), label(required) |
| essentials/products | `proofpoint_essentials_products_product_patch` | PATCH /orgs/{domain}/products/{label} | domain(required), label(required), body(required) |
| essentials/products | `proofpoint_essentials_products_products_post` | POST /orgs/{domain}/products | domain(required), body(required) |
| essentials/reporting | `proofpoint_essentials_reporting_get_reporting_period` | GET /reporting/{domain}/{period} | domain(required), period(required) |
| essentials/reporting | `proofpoint_essentials_reporting_get_reporting_period_by_direction` | GET /reporting/{domain}/{period}/{direction} | domain(required), period(required), direction(required) |
| essentials/sender lists | `proofpoint_essentials_sender_lists_delete_group_lists` | DELETE /orgs/{domain}/groups/{group}/sender-lists | domain(required), group(required) |
| essentials/sender lists | `proofpoint_essentials_sender_lists_delete_sender_lists` | DELETE /orgs/{domain}/sender-lists | domain(required) |
| essentials/sender lists | `proofpoint_essentials_sender_lists_delete_user_lists` | DELETE /orgs/{domain}/users/{user}/sender-lists | domain(required), user(required) |
| essentials/sender lists | `proofpoint_essentials_sender_lists_get_group_lists` | GET /orgs/{domain}/groups/{group}/sender-lists | domain(required), group_id(required) |
| essentials/sender lists | `proofpoint_essentials_sender_lists_get_sender_lists` | GET /orgs/{domain}/sender-lists | domain(required) |
| essentials/sender lists | `proofpoint_essentials_sender_lists_get_user_lists` | GET /orgs/{domain}/users/{user}/sender-lists | domain(required), user(required) |
| essentials/sender lists | `proofpoint_essentials_sender_lists_patch_group_sender_lists` | PATCH /orgs/{domain}/groups/{group}/sender-lists | domain(required), group(required), body(required) |
| essentials/sender lists | `proofpoint_essentials_sender_lists_patch_sender_lists` | PATCH /orgs/{domain}/sender-lists | domain(required), body(required) |
| essentials/sender lists | `proofpoint_essentials_sender_lists_patch_user_sender_lists` | PATCH /orgs/{domain}/users/{user}/sender-lists | domain(required), user(required), body(required) |
| essentials/sender lists | `proofpoint_essentials_sender_lists_post_group_lists` | POST /orgs/{domain}/groups/{group}/sender-lists | domain(required), group(required), body(required) |
| essentials/sender lists | `proofpoint_essentials_sender_lists_post_sender_lists` | POST /orgs/{domain}/sender-lists | domain(required), body(required) |
| essentials/sender lists | `proofpoint_essentials_sender_lists_post_user_lists` | POST /orgs/{domain}/users/{user}/sender-lists | domain(required), user(required), body(required) |
| essentials/settings | `proofpoint_essentials_settings_delete_azure_settings` | DELETE /orgs/{domain}/settings/azure | domain(required) |
| essentials/settings | `proofpoint_essentials_settings_get_azure_settings` | GET /orgs/{domain}/settings/azure | domain(required) |
| essentials/settings | `proofpoint_essentials_settings_put_azure_settings` | PUT /orgs/{domain}/settings/azure | domain(required), body(required) |
| essentials/stats | `proofpoint_essentials_stats_partner_stats_all_orgs` | GET /stats/{domain}/partner/orgs | domain(required), period(optional), page(optional), page_size(optional) |
| essentials/stats | `proofpoint_essentials_stats_partner_stats_single_org` | GET /stats/{domain}/partner | domain(required), period(optional), page(optional), page_size(optional) |
| essentials/sync exemptions | `proofpoint_essentials_sync_exemptions_delete_all_azure_exemptions` | DELETE /orgs/{domain}/settings/azure/exemptions | domain(required) |
| essentials/sync exemptions | `proofpoint_essentials_sync_exemptions_delete_azure_exemptions` | DELETE /orgs/{domain}/settings/azure/exemptions/{user} | domain(required), user(required) |
| essentials/sync exemptions | `proofpoint_essentials_sync_exemptions_get_azure_exemptions` | GET /orgs/{domain}/settings/azure/exemptions | domain(required) |
| essentials/sync exemptions | `proofpoint_essentials_sync_exemptions_put_azure_exemptions` | PUT /orgs/{domain}/settings/azure/exemptions | domain(required), body(required) |
| essentials/token | `proofpoint_essentials_token_post_token` | POST /token/{domain} | domain(required), body(required) |
| essentials/users | `proofpoint_essentials_users_delete_user` | DELETE /orgs/{domain}/users/{user} | domain(required), user(required) |
| essentials/users | `proofpoint_essentials_users_get_user` | GET /orgs/{domain}/users/{user} | domain(required), user(required) |
| essentials/users | `proofpoint_essentials_users_get_users` | GET /orgs/{domain}/users | domain(required) |
| essentials/users | `proofpoint_essentials_users_post_user` | POST /orgs/{domain}/users | domain(required), body(required) |
| essentials/users | `proofpoint_essentials_users_put_user` | PUT /orgs/{domain}/users/{user} | domain(required), user(required), body(required) |
| tap/campaign | `proofpoint_tap_campaign_get_campaign` | GET /v2/campaign/{campaign_id} | campaign_id(required) |
| tap/campaign | `proofpoint_tap_campaign_list_ids` | GET /v2/campaign/ids | interval(required), size(optional), page(optional) |
| tap/forensics | `proofpoint_tap_forensics_get_forensics` | GET /v2/forensics | threat_id(optional), campaign_id(optional), include_campaign_forensics(optional) |
| tap/people | `proofpoint_tap_people_get_top_clickers` | GET /v2/people/top-clickers | window(required), size(optional), page(optional) |
| tap/people | `proofpoint_tap_people_get_vap` | GET /v2/people/vap | window(required), size(optional), page(optional) |
| tap/tap | `proofpoint_tap_tap_get_all_threats` | GET /v2/siem/all | since_seconds(optional), since_time(optional), interval(optional), threat_status(optional), format(optional) |
| tap/tap | `proofpoint_tap_tap_get_clicks_blocked` | GET /v2/siem/clicks/blocked | since_seconds(optional), since_time(optional), interval(optional), threat_status(optional) |
| tap/tap | `proofpoint_tap_tap_get_clicks_permitted` | GET /v2/siem/clicks/permitted | since_seconds(optional), since_time(optional), interval(optional), threat_status(optional) |
| tap/tap | `proofpoint_tap_tap_get_messages_blocked` | GET /v2/siem/messages/blocked | since_seconds(optional), since_time(optional), interval(optional), threat_status(optional) |
| tap/tap | `proofpoint_tap_tap_get_messages_delivered` | GET /v2/siem/messages/delivered | since_seconds(optional), since_time(optional), interval(optional), threat_status(optional) |
| tap/threats | `proofpoint_tap_threats_get_by_id` | GET /v2/threat/summary/{threat_id} | threat_id(required) |
| tap/url_defense | `proofpoint_tap_url_defense_decode` | POST /v2/url/decode | body(required) |

## 测试示例

```bash
# Health check
curl -s http://localhost:8080/health

# Call a TAP tool via the MCP protocol (streamable HTTP) — requires an
# initialize handshake first per the MCP spec; abbreviated example below
# shows the tool-call request body only:
curl -s -X POST http://localhost:8080/mcp \
  -H "X-Proofpoint-Tap-Service-Principal: <service-principal>" \
  -H "X-Proofpoint-Tap-Service-Secret: <service-secret>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: <session-id-from-initialize>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "proofpoint_tap_tap_get_all_threats",
      "arguments": {"interval": "PT1H"}
    }
  }'
```

**Live-verified** (2026-08-03), without a real Proofpoint account (none was supplied for this task): every one of the 12 TAP tools was called through this running server with intentionally invalid credentials (`fake:fake`) against the real `https://tap-api-v2.proofpoint.com` host. All 12 returned `Proofpoint API error 401: Error : Service Id / Credentials authentication failed` — proving the full request pipeline (header parsing → contextvar isolation → client construction → Basic Auth encoding → real network call → error parsing) works end-to-end, and that every tool's path/param shape is recognized by the real API server (a wrong path would 404, not 401). Structural tests also confirmed: the blanket 401 gate rejects requests with neither credential set; supplying only TAP credentials and calling an Essentials tool correctly returns `NO_ESSENTIALS_TOKEN` (and vice versa) rather than crashing or leaking the wrong client; `tools/list` returns exactly 89 tools.

No Proofpoint credentials (TAP or Essentials) were provided with this task, so a live call against real account data has not been performed for either product — only the negative-credential (401) path above.

## API Reference

**TAP:**
- Threat Insight Dashboard API overview: https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation
- SIEM API: https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/SIEM_API
- Campaign API: https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/Campaign_API
- People API: https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/People_API
- Forensics API: https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/Forensics_API
- URL Decoder API: https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/URL_Decoder_API
- Threats API (login-gated — see Known Gaps): https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/Threats_API

**Essentials:**
- Official OpenAPI 3.0 spec (downloadable): https://us1.proofpointessentials.com/apidocs/apidocs/docs
- Essentials admin guide: https://help.proofpoint.com/Proofpoint_Essentials

## Known Gaps

- **Community repo's `dlp`, `policy`, `quarantine`, `smart_search`, `events` categories (13 tools) were dropped entirely** — confirmed fabricated/nonexistent against both live testing and official docs. See Verification Methodology above.
- **Reports/Dash Reports API was discovered but not built.** It's a real, separate Proofpoint product at `threatprotection-api.proofpoint.com` with its own OAuth2 `client_credentials` auth flow (`POST https://auth.proofpoint.com/v1/token`) and ~30 endpoints (Executive Summary, Effectiveness Reports, Organization Reports, Threat Landscape Reports). This is new scope beyond fixing the existing 11 TAP categories from the community repo, and wasn't part of this task's original request — flag separately if reporting/dashboard data is actually needed.
- **"Threats API" doc page is login-gated.** `help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/Threats_API` redirects to a Proofpoint account sign-in wall. The one tool in this category (`proofpoint_tap_threats_get_by_id`, `GET /v2/threat/summary/{threat_id}`) is confirmed live (401, route recognized) but its full parameter/response schema could not be cross-checked against the official doc — if it doesn't behave as expected against a real threat ID, that's the first place to look.
- **Supplier Threat Protection API was not evaluated** — it's one of the 8 official TAP sub-APIs but has no corresponding tool in the community repo to begin with, so it was out of scope for this correction pass. Not built.
- **No live self-test against real account data.** This task did not come with a Proofpoint test account/credentials (unlike most other vendor builds in this program). Only negative-credential (401, route-recognized) verification has been performed — see 测试示例 above.
- **`domain` param naming (Essentials).** Per the official OpenAPI spec, most Essentials paths use `{domain}` as a path segment that actually identifies the *organization* being operated on (not always a literal email domain) — this matches the vendor's own spec/terminology exactly, not a naming choice made here.
- **Essentials write operations are destructive/irreversible where the underlying HTTP verb is DELETE** (e.g. `proofpoint_essentials_domains_delete_domain`, `proofpoint_essentials_users_delete_user`, `proofpoint_essentials_orgs_delete_org`) — treat these as irreversible against a real tenant and confirm with a human before invoking.
