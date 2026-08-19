# proofpoint-mcp

MCP server for **Proofpoint** — wraps two distinct Proofpoint products/APIs behind one MCP server: **TAP (Targeted Attack Protection)**, threat/campaign/people-risk intelligence, and **Essentials**, the Proofpoint Essentials tenant/user/domain administration API.

> **Tool Scope note (2026-08-07):** the tool surface was trimmed from 28 to
> 15 tools. The parent ClickUp task's stated primary use case is **email
> security account creation / synchronization**, so all 12 Essentials
> account/org/domain/user management tools are kept in full, while TAP
> (threat analytics) is trimmed to one representative tool per category:
> `get_all_threats`, `get_vap`, and `url_defense_decode`. Dropped as lower
> priority for the account-provisioning use case: campaign tracking,
> forensics, per-category click/message breakdowns (SIEM
> clicks-blocked/permitted, messages-blocked/delivered), Azure AD sync
> exemptions, and threat-by-id lookup. See the Scope section below for the
> full breakdown.

## Overview

- Stateless HTTP service. No credentials are ever persisted — each request supplies its own credentials via headers, used only for the lifetime of that single request.
- Supports concurrent requests; per-request credential isolation is done via two independent Python `contextvars` (one per product), not a global/shared client instance.
- Entry points: `POST /mcp` (MCP protocol) and `GET /health` (health check).
- Default port: `8080` (configurable via `MCP_HTTP_PORT`).
- **This server wraps two genuinely separate Proofpoint products with two separate credential types.** A caller using only one product's tools does not need to also supply the other product's credentials — see Authentication below.

## Scope

**15 tools**: 3 for TAP, 12 for Proofpoint Essentials. Trimmed down from a
28-tool build (12 TAP + 16 Essentials) on 2026-08-07, which itself was
trimmed from an original 89-tool build (12 TAP + 77 Essentials) on
2026-08-04.

No official Proofpoint MCP server exists (confirmed by searching both the `wyre-technology` and `MSPbotsAI` GitHub orgs, and Proofpoint's own docs/marketplace). A community project, [`wyre-technology/proofpoint-mcp`](https://github.com/wyre-technology/proofpoint-mcp), exists and claims TAP + "Essentials" coverage, but its actual code only ever calls the TAP host (`tap-api-v2.proofpoint.com`) — it has no Essentials API integration at all despite the README's claim. This server is a from-scratch build, not a fork.

- **Essentials (12 tools, kept in full)**: the parent ClickUp task explicitly emphasizes **email security account creation / synchronization** as the primary use case, so every Essentials category directly supporting that flow is kept in its entirety: `users` (5 tools: get/list/create/update/delete — this *is* account creation), `orgs` (3: get/create/update — a user must belong to an org), `domains` (3: list/create/get — a user's email domain must exist first), and `me` (1, connectivity self-test). The `sync_exemptions` category (4 tools: get/set/delete Azure AD sync exemptions) was dropped on 2026-08-07 as a lower priority than the core account-provisioning tools for this trim. The earlier 77-tool Essentials build additionally generated full CRUD from Proofpoint's official OpenAPI 3.0 spec (`https://us1.proofpointessentials.com/apidocs/apidocs/docs`) across DKIM, Authentication (IdP/MFA/login settings), Sender Lists, Billing, Licensing, Products, Reporting, Settings, Features, Email Tagging, Token, Endpoints, and Domain Verification (13 categories, ~61 tools) — all removed as unrelated to the account-creation/sync task.
- **TAP (3 tools, trimmed from 12 on 2026-08-07)**: hand-built from Proofpoint's official Threat Insight Dashboard API documentation (`help.proofpoint.com`) plus live endpoint verification, **not** ported as-is from the community repo. See **Verification Methodology** below for the original 12-tool selection rationale (why that was already a much smaller set than the community repo's 38 TAP tools). As of 2026-08-07, TAP was trimmed further to one representative tool per category, since threat analytics is secondary to this server's primary account-provisioning use case: `tap.get_all_threats` (SIEM, kept), `people.get_vap` (kept; `people.get_top_clickers` dropped), `url_defense.decode` (kept, unchanged — it was already this category's only tool). Dropped entirely in this pass: `campaign` (2 tools: get_campaign, list_ids), `forensics` (1 tool: get_forensics), `threats` (1 tool: get_by_id), and the `tap` category's per-type SIEM breakdowns (`get_clicks_blocked`, `get_clicks_permitted`, `get_messages_blocked`, `get_messages_delivered` — `get_all_threats` already covers this data in one combined call).

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

**Net result**: 12 TAP tools, every one of which returns `401` (route recognized, credentials rejected) when live-tested against `https://tap-api-v2.proofpoint.com` with placeholder credentials — no tool in this server points at a nonexistent or fabricated endpoint. (As of the 2026-08-07 trim, only 3 of these 12 remain in this server — `tap.get_all_threats`, `people.get_vap`, `url_defense.decode` — see Scope above; the other 9 are still real, verified endpoints and could be re-added from this table if needed.)

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
- `GET /health` — health check, returns `{"status": "ok"}`. Pure local liveness probe; does not depend on either Proofpoint API being reachable.

## Tool List

Tool names are `proofpoint_<product>_<category>_<operation>`. Essentials tool signatures/params were generated directly from Proofpoint's own OpenAPI spec (`domain` is the Essentials org identifier path parameter used throughout, per that spec's own convention — not a DNS domain in most calls). `body` parameters for create/update/patch endpoints are accepted as a generic `dict` matching the corresponding OpenAPI request schema.

| Category | Tool | Method + Path | Params |
|---|---|---|---|
| essentials_domains | `proofpoint_essentials_domains_get_domain` | GET /orgs/{domain}/domains/{targetDomain} | domain(required), target_domain(required) |
| essentials_domains | `proofpoint_essentials_domains_get_domains` | GET /orgs/{domain}/domains | domain(required) |
| essentials_domains | `proofpoint_essentials_domains_post_domain` | POST /orgs/{domain}/domains | domain(required), body(required) |
| essentials_me | `proofpoint_essentials_me_get_me` | GET /me | none |
| essentials_orgs | `proofpoint_essentials_orgs_get_org` | GET /orgs/{domain} | domain(required) |
| essentials_orgs | `proofpoint_essentials_orgs_patch_org` | PATCH /orgs/{domain} | domain(required), body(required) |
| essentials_orgs | `proofpoint_essentials_orgs_post_org` | POST /orgs/{domain}/orgs | domain(required), body(required) |
| essentials_users | `proofpoint_essentials_users_delete_user` | DELETE /orgs/{domain}/users/{user} | domain(required), user(required) |
| essentials_users | `proofpoint_essentials_users_get_user` | GET /orgs/{domain}/users/{user} | domain(required), user(required) |
| essentials_users | `proofpoint_essentials_users_get_users` | GET /orgs/{domain}/users | domain(required) |
| essentials_users | `proofpoint_essentials_users_post_user` | POST /orgs/{domain}/users | domain(required), body(required) |
| essentials_users | `proofpoint_essentials_users_put_user` | PUT /orgs/{domain}/users/{user} | domain(required), user(required), body(required) |
| tap/people | `proofpoint_tap_people_get_vap` | GET /v2/people/vap | window(required), size(optional), page(optional) |
| tap/tap | `proofpoint_tap_tap_get_all_threats` | GET /v2/siem/all | since_seconds(optional), since_time(optional), interval(optional), threat_status(optional), format(optional) |
| tap/url_defense | `proofpoint_tap_url_defense_decode` | POST /v2/url/decode | body(required) |

**Removed on 2026-08-07** (were previously in this table; see Scope above for rationale): `essentials_sync_exemptions` (4 tools: get/put/delete/delete-all Azure AD exemptions), `tap/campaign` (`get_campaign`, `list_ids`), `tap/forensics` (`get_forensics`), `tap/threats` (`get_by_id`), `tap/people.get_top_clickers`, and `tap/tap`'s `get_clicks_blocked`, `get_clicks_permitted`, `get_messages_blocked`, `get_messages_delivered`.

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

**Structural self-test (2026-08-07, after the 28→15 tool trim)**: server started locally, `GET /health` confirmed OK, then an MCP `streamablehttp_client` + `ClientSession` did a full `initialize()` + `tools/list()` against it with dummy (non-functional) values for all 5 credential headers (just enough to pass the transport-level 401 gate). Result: exactly 15 tools returned, no duplicate names, matching the Scope section's list exactly.

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

## Vendor MCP SOP Compliance Notes (2026-08-19 pass)

- **Error format changed**: tool errors were plain `"Error: ..."` strings; they are now a
  structured JSON envelope `{"error": {"code", "message", "retryable"}}` with `code` drawn
  from the fixed vocabulary (`not_configured`/`unauthorized`/`not_found`/`invalid_argument`/
  `rate_limited`/`upstream_error`). Any downstream consumer that pattern-matched on the old
  `"Error: "` prefix needs to switch to parsing this JSON envelope instead.
- **Responses are now compact JSON** (`dump_json_capped`, `ensure_ascii=False`, no `indent`),
  capped at ~20,000 chars with truncation + `original_count` reported if a result would
  exceed that — previously `json.dumps(..., indent=2)` returned uncapped, indent-padded JSON.
- **Retry/backoff added**: outbound calls to both Proofpoint APIs now retry up to 3 times on
  `429`/`5xx` with exponential backoff (capped 20s, respects `Retry-After`); previously there
  was no retry logic and a fresh `httpx.AsyncClient` was opened per call instead of reusing a
  pooled connection.
- **`proofpoint_tap_people_get_vap`'s `size` param is now clamped** to a default of 50 and a
  hard cap of 200 (applied here, not by Proofpoint). Proofpoint's own People API docs give no
  documented maximum for this endpoint's `size` (unlike the sibling top-clickers endpoint,
  which documents 200) and default to 1000 if omitted — too large for a token-bounded tool
  result, so this server applies the Vendor MCP SOP's fallback ceiling instead of trusting
  the undocumented vendor default. No other tool in this server takes a list-size/pagination
  parameter: `essentials_domains_get_domains` and `essentials_users_get_users` return an
  org's full domain/user list with no pagination parameters in Proofpoint's own v1 API (per
  `https://us1.proofpointessentials.com/api/v1/docs/index.php`), so oversized results are
  bounded only by this server's own `dump_json_capped` truncation, not a vendor-side limit.
- **Tool annotations added** (`readOnlyHint`/`destructiveHint`/`idempotentHint` per
  `mcp.types.ToolAnnotations`) and a service-level `instructions` string was added to the
  FastMCP server describing how the TAP and Essentials tool groups relate.
- No parameter was renamed and no tool was added/removed in this pass — the tool
  count/names/required-params in the table above are unchanged.

## Known Gaps

- **Trimmed from 28 to 15 tools on 2026-08-07**, per the parent ClickUp
  task's stated primary use case (email security account creation /
  synchronization). Essentials kept in full (12 tools: users, orgs,
  domains, me); `sync_exemptions` (4 tools) dropped. TAP cut to one
  representative tool per category (3 tools: `get_all_threats`, `get_vap`,
  `url_defense_decode`); `campaign`, `forensics`, `threats`, the per-type
  SIEM click/message breakdowns, and `people.get_top_clickers` were
  dropped as lower priority for account provisioning. See the Scope
  section above for the full rationale; the removed tools' code is still
  in git history if a future task needs them back.
- **Trimmed from 89 to 28 tools on 2026-08-04.** TAP was already minimal
  (12 tools, unchanged). Essentials was cut from a full-API 77-tool build
  down to 16 tools covering the original ClickUp task's stated need
  (account creation + synchronization) — see the Scope section above for
  the exact category rationale and the full list of the 13 removed
  Essentials categories (~61 tools: Authentication, Billing, DKIM, Domain
  Verification, Email Tagging, Endpoints, Features, Licensing, Package,
  Products, Reporting, Sender Lists, Settings, Stats, Token). If a removed
  category is needed later, Proofpoint's own OpenAPI spec (linked below)
  still documents its exact operations and they can be re-added the same
  way the kept tools were generated.
- **Community repo's `dlp`, `policy`, `quarantine`, `smart_search`, `events` categories (13 tools) were dropped entirely** — confirmed fabricated/nonexistent against both live testing and official docs. See Verification Methodology above.
- **Reports/Dash Reports API was discovered but not built.** It's a real, separate Proofpoint product at `threatprotection-api.proofpoint.com` with its own OAuth2 `client_credentials` auth flow (`POST https://auth.proofpoint.com/v1/token`) and ~30 endpoints (Executive Summary, Effectiveness Reports, Organization Reports, Threat Landscape Reports). This is new scope beyond fixing the existing 11 TAP categories from the community repo, and wasn't part of this task's original request — flag separately if reporting/dashboard data is actually needed.
- **"Threats API" doc page is login-gated.** `help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/Threats_API` redirects to a Proofpoint account sign-in wall. The one tool in this category (`proofpoint_tap_threats_get_by_id`, `GET /v2/threat/summary/{threat_id}`) is confirmed live (401, route recognized) but its full parameter/response schema could not be cross-checked against the official doc — if it doesn't behave as expected against a real threat ID, that's the first place to look.
- **Supplier Threat Protection API was not evaluated** — it's one of the 8 official TAP sub-APIs but has no corresponding tool in the community repo to begin with, so it was out of scope for this correction pass. Not built.
- **No live self-test against real account data.** This task did not come with a Proofpoint test account/credentials (unlike most other vendor builds in this program). Only negative-credential (401, route-recognized) verification has been performed — see 测试示例 above.
- **`domain` param naming (Essentials).** Per the official OpenAPI spec, most Essentials paths use `{domain}` as a path segment that actually identifies the *organization* being operated on (not always a literal email domain) — this matches the vendor's own spec/terminology exactly, not a naming choice made here.
- **Essentials write operations are destructive/irreversible where the underlying HTTP verb is DELETE** — `proofpoint_essentials_users_delete_user` (the only DELETE tool remaining after the 2026-08-07 trim removed the 2 `sync_exemptions` delete tools) — treat this as irreversible against a real tenant and confirm with a human before invoking.
