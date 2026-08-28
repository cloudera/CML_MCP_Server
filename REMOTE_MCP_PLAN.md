# Remote, Multi-Tenant MCP Server for Cloudera AI Workbench — Plan

**Branch:** `feat/remote-multitenant-mcp`
**Status:** implementation in progress. Workbench-side surface (`cloudera-sense@7209d48fdb`) has landed the OAuth 2.1 AS on `services/web`, the `/api/v2/auth/exchange` endpoint on `services/api`, and the Helm templates for the two-container MCP pod. MCP-side sidecar + `http_server.py` rewire are in this commit.

## Context

The current MCP server ([`cai_workbench_mcp_server/stdio_server.py`](cai_workbench_mcp_server/stdio_server.py) and [`cai_workbench_mcp_server/http_server.py`](cai_workbench_mcp_server/http_server.py)) reads one workbench host + one API key + one project_id from Docker secrets / env at process start, and every one of its ~100 `@mcp.tool()` functions calls the same global `get_config()` on entry. Fine for a single user running the stdio server locally, but it makes the HTTP server single-tenant: every request runs as whatever principal owns the mounted secrets.

We want a remote MCP server, deployed in the same Kubernetes cluster as Cloudera AI Workbench (the "cloudera-sense" monorepo at `~/cldr/repos/github.infra.cloudera.com/Sense/cloudera-sense`), that many users can point their MCP clients (Claude Code, Claude Desktop, Cursor, VS Code) at. Every tool call must run as the calling user against the workbench, using the same two auth mechanisms the workbench itself already supports:

- **OAuth 2.1** — same mechanism the browser UI and APIv1 use today (SAML/LDAP/Knox → fingerprint-bound web JWT). We expose this to MCP clients as **MCP-spec OAuth 2.1** (Protected Resource Metadata + Authorization Server + PKCE + Dynamic Client Registration), delegated into the workbench's existing SSO. The AS lives on `services/web` and mints RS256 access tokens with `iss=workbench-web`, `aud=cai-workbench-mcp`.
- **Bearer/JWT** — same mechanism APIv2 uses today: user API keys (`hex64.hex64`) or web JWTs, validated by `/api/v2/auth/validate_key`. MCP clients send these directly in `Authorization: Bearer`.
- **CDP IAM workload auth tokens** — RS256 JWTs minted by Cloudera's central IAM (Thunderhead) service, obtained by an operator via `cdp iam generate-workload-auth-token --workload-name DE --profile <env>`. The MCP client sends the token in `Authorization: Bearer` exactly like the other two shapes. Verification is delegated to the workbench (`/api/v2/auth/exchange` handler holds the CDP IAM JWKS URL / issuer / audience config); the sidecar just classifies the token by its `iss` and forwards to the exchange endpoint with a `token_type=cdp_iam_workload` discriminator so the handler picks the right verification path. The `sub` claim is the workbench username; the exchange mints the same short-lived opaque APIv2 key the OAuth branch does. Empty `MCP_IAM_ISSUERS` = feature disabled (default).

The caller's identity is threaded through to the `cmlapi` SDK on every tool call — one identity end to end, no impersonation, no per-user API-key vault to run. Upload / download tools stay as-is semantically (they manipulate files inside remote workbench projects via the workbench Files API, not the caller's local disk).

## Design

### Sidecar architecture

Auth is factored out of the MCP server into a **translation sidecar** — a second container in the same pod. The sidecar owns the entire authenticated boundary; the MCP server behind it stays a plain, unauthenticated FastMCP tool host that trusts a purpose-named internal header.

```
Client ──HTTPS──▶ Istio/Knox ──▶ pod:8080 (translation_sidecar.py)
                                    │
                                    ├─ Classify Authorization header:
                                    │    • hex64.hex64            → APIv2 API key
                                    │    • JWT, iss=workbench-AS  → MCP OAuth access token
                                    │    • JWT, iss ∈ IAM issuers → CDP IAM workload auth token
                                    │    • JWT, iss=workbench-web → APIv2 web JWT
                                    ├─ Verify:
                                    │    • OAuth  → RS256 signature via web AS public key
                                    │               + iss=workbench-web + aud=cai-workbench-mcp
                                    │    • APIv2  → POST /api/v2/auth/validate_key
                                    │    • CDP IAM → delegated to workbench /exchange handler
                                    │               (sidecar never touches CDP IAM JWKS)
                                    ├─ Downstream token:
                                    │    • OAuth  → POST /api/v2/auth/exchange → opaque APIv2 key
                                    │              (hex64.hex64, short-lived, bound to same subject)
                                    │    • CDP IAM → POST /api/v2/auth/exchange with
                                    │               token_type=cdp_iam_workload → same shape
                                    │    • APIv2  → forward as-is
                                    ├─ Cache (sha256(caller-bearer) → apiv2-token, principal, expiry; TTL 60s)
                                    ├─ Rewrite headers:
                                    │    • strip inbound Authorization
                                    │    • inject X-CAI-Downstream-Bearer: <apiv2-token>
                                    │    • inject X-CAI-Principal: <username>
                                    └─ Reverse-proxy to 127.0.0.1:8081 (http_server.py)
                                                                             │
                                                                             └─ setup_client(host, apiv2-token) → cmlapi
```

Two containers, one pod, distinct listen hosts:

| Container | Entry point | Binds to | Purpose |
|---|---|---|---|
| `translation-sidecar` | `cai-workbench-mcp-sidecar` | `0.0.0.0:8080` (pod's public port) | Auth boundary: MCP OAuth discovery, token verification, token exchange, reverse proxy |
| `mcp-server` | `cai-workbench-mcp-http` | `127.0.0.1:8081` (loopback only) | FastMCP tool host; trusts `X-CAI-Downstream-Bearer` |

### Special header contract — why a new one, not `Authorization`

The sidecar **strips** the inbound `Authorization` header and injects a distinct one:

```
X-CAI-Downstream-Bearer: <apiv2-token>
X-CAI-Principal:         <workbench username>   (informational, for logs / audit)
```

Rationale: on `127.0.0.1:8081`, an incoming `Authorization` header would be indistinguishable from someone `kubectl exec`'ing into the pod and hitting MCP directly. With a purpose-named header the MCP server hard-refuses any request that omits it — defense in depth against a compromised sidecar container or lateral movement inside the pod. `X-CAI-Principal` is not trusted for authorization decisions; it's there so MCP logs carry the caller's username without having to decode the bearer.

### MCP server changes — minimal

- Introduce `cai_workbench_mcp_server/auth/context.py` with a `contextvars.ContextVar` called `request_config`.
- Add a tiny Starlette middleware inside `http_server.py` that:
  - Reads `X-CAI-Downstream-Bearer` from the incoming request.
  - Refuses (`401` + a stern log line) any request missing it — this port is only ever reached over the pod's loopback via the sidecar.
  - Sets `request_config = {"host": WORKBENCH_HOST, "api_key": <bearer>, "project_id": None, "team": None}` for the request's duration.
- Rewrite `get_config()` to return `request_config.get()` in HTTP mode (never fall back to module-level env vars — that would be the current single-tenant bug).
- The single choke point [`src/functions/http_helpers.py`](cai_workbench_mcp_server/src/functions/http_helpers.py) `setup_client(host, api_key)` already receives host + key as arguments and sets the `Authorization: Bearer` header on the cmlapi client — no change needed. Every tool automatically picks up the caller's identity.
- Also bind the MCP server to `127.0.0.1` by default when running in HTTP mode (env override permitted for local development).

FastMCP no longer needs a `RemoteAuthProvider` or any auth wiring at all inside `http_server.py`. Discovery and challenges live in the sidecar.

`stdio_server.py` is untouched; local users still get env-var config.

### Translation sidecar — `translation_sidecar.py`

A single-file **Starlette + httpx ASGI reverse proxy** run under uvicorn. No FastMCP dependency — it isn't an MCP server, it's a proxy that speaks HTTP.

Responsibilities:

1. **MCP-spec OAuth 2.1 surface.** Owns:
   - `GET /.well-known/oauth-protected-resource` — RFC 9728 metadata pointing at the workbench AS.
   - `WWW-Authenticate: Bearer resource_metadata="https://mcp.<domain>/.well-known/oauth-protected-resource"` on every 401.
   - Optionally proxies `/.well-known/oauth-authorization-server` from the workbench AS to smooth out client quirks.

2. **Token classification.**

   **PoC dispatch (current implementation).** For proof-of-concept work the sidecar dispatches purely on the `Authorization` **scheme**, not on token shape or issuer:
   - `Authorization: BearerV2 <token>` → treat as an APIv2 credential (API key or workbench web JWT). Verified via `/api/v2/auth/validate_key` and forwarded verbatim as the downstream bearer.
   - `Authorization: Bearer <token>` → treat as a CDP IAM workload auth token. The sidecar does **no** signature verification; it forwards the raw JWT to `/api/v2/auth/exchange` with `token_type=cdp_iam_workload` and the workbench decodes `sub` to mint a short-lived APIv2 key. Rationale: JWKS fetch for CDP IAM (thunderhead consoleauth) requires `x-altus-auth` request signing that the workbench doesn't have provisioned yet; deferring signature verification to the workbench's user-lookup gate is the PoC-scope compromise.
   - Any other scheme (or a missing header) → 401 with the discovery challenge.

   The MCP OAuth 2.1 verification helper (`_validate_oauth`) is preserved in the code but is unreachable under the PoC dispatch — it will be reintroduced by either routing `Bearer` back to it (and giving IAM its own scheme) or by adding a per-token issuer sniff in front of the scheme check.

   **Target dispatch (issuer-based, still on the roadmap).** Once JWKS-based verification is wired for both OAuth and CDP IAM the sidecar will fall back to inspecting the token itself:
   - Matches `^[0-9a-f]{64}\.[0-9a-f]{64}$` → APIv2 API key.
   - Parses as JWT and inspects `iss` → matches `MCP_OAUTH_ISSUER` → MCP OAuth access token; matches an entry in `MCP_IAM_ISSUERS` (comma-separated list) → CDP IAM workload auth token; otherwise → APIv2 web JWT.
   - Anything else → 401 with the discovery challenge.

   The `classify_token` helper implementing this target dispatch is already in the codebase and covered by unit tests, so switching back is a one-liner in `_forward`.

3. **Verification.**
   - **APIv2 key / web JWT:** `POST {WORKBENCH_HOST}/api/v2/auth/validate_key` (that endpoint bypasses the audience check — see [`services/api/srv/auth/auth.go`](../github.infra.cloudera.com/Sense/cloudera-sense/services/api/srv/auth/auth.go)). Response provides the principal.
   - **MCP OAuth access token:** RS256 signature verified against the web AS public key (JWKS from `/oauth/jwks` on the web service, or the mounted `web-tls2` public key at `/ca/web/tls.pub`); check `iss == workbench-web` and `aud == cai-workbench-mcp`.
   - **CDP IAM workload auth token:** verification is **delegated to the workbench**. The sidecar performs no signature check on this branch — the workbench's `/api/v2/auth/exchange` handler holds the CDP IAM JWKS URL, expected issuer, and (optional) audience config, and is the authoritative verifier. Rationale: keeps CDP IAM verification material (HTTP egress to `iamapi.<region>.altus.cloudera.com`, `kid` cache, rotation handling) on one workbench API pod instead of duplicated in every sidecar container; the sidecar is a proxy, verification belongs behind it.

4. **Downstream token.**
   - APIv2 caller: keep the caller's token verbatim as the downstream bearer.
   - OAuth caller: `POST {WORKBENCH_HOST}/api/v2/auth/exchange` with the OAuth token → receive a short-lived opaque APIv2 API key (`hex64.hex64`, ~10 min TTL) bound to the same subject. The exchange handler self-verifies the JWT against the web AS public key, so APIv2's normal `Authenticate()` bypasses credential extraction for this path only (documented contract in `srv/auth/auth.go`).
   - CDP IAM caller: same endpoint, request body carries a `token_type: "cdp_iam_workload"` discriminator. The handler branches on that field, verifies against the CDP IAM JWKS, resolves `sub` → workbench username via the same `users.GetUserByUsername` helper as the OAuth branch, and mints the same short-lived APIv2 key. Response shape is identical to the OAuth branch. Back-compat: omitted / empty / `"mcp_oauth"` value = existing OAuth verification.

5. **In-memory cache.** A plain `dict` on the sidecar process, keyed by `sha256(caller-bearer)`:
   - Value: `(downstream_bearer, principal, expires_at)`.
   - TTL 60 s or `min(remaining_ttl_of_downstream_token, 60s)`, whichever is shorter.
   - Sized for the workbench scale (≤ ~1000 users). No external cache, no Redis; a `functools.lru_cache`-style bounded dict is enough. If the cache line's downstream token has expired, drop it and re-verify.
   - On any downstream 401 during the request, evict the line and return 401 to the client with the discovery challenge (so the client re-auths).

6. **Reverse proxy.** For any non-well-known path, forward the (rewritten) request to `http://127.0.0.1:8081` using `httpx.AsyncClient`. Handles Streamable HTTP transparently — both the JSON-RPC POST and any long-lived SSE GET are just byte-forwarded after header rewriting.

7. **Failure translation.**
   - Missing / malformed / unverified bearer → 401 + `WWW-Authenticate: Bearer resource_metadata=...`.
   - Downstream (validate_key / exchange) returns 401 → 401 to client (same challenge).
   - Downstream returns 5xx → 502 to client.
   - Anything else in the sidecar → 500 with a log line; never leak the caller's token in errors.

The sidecar reads its config from env vars at start: `WORKBENCH_HOST`, `MCP_UPSTREAM_URL` (default `http://127.0.0.1:8081`), `MCP_OAUTH_ISSUER`, `MCP_OAUTH_JWKS_URL`, `MCP_OAUTH_AUDIENCE` (default `cai-workbench-mcp`), `MCP_IAM_ISSUERS` (comma-separated list of accepted CDP IAM issuer strings; empty = IAM path disabled), `MCP_CACHE_TTL_SECONDS` (default 60), `LISTEN_HOST` / `LISTEN_PORT` (default `0.0.0.0:8080`). The workbench Helm chart injects `WORKBENCH_HOST` and the OAuth issuer/JWKS URLs at deploy time. `MCP_IAM_ISSUERS` is opt-in and defaults empty. The CDP IAM verification material — JWKS URL, issuer, optional audience — lives on the workbench API pod (`CDP_IAM_JWKS_URL`, `CDP_IAM_ISSUER`, `CDP_IAM_AUDIENCE`), not on the sidecar.

### Kubernetes / Helm

Landed in [`cloudera-sense@7209d48fdb`](../github.infra.cloudera.com/Sense/cloudera-sense/) under [`packaging/chart/cdsw-entrypoints/templates/`](../github.infra.cloudera.com/Sense/cloudera-sense/packaging/chart/cdsw-entrypoints/templates/):

- `mcp.yaml` — `Deployment` with three containers, gated on `MCP.Enabled`:
  - `translation-sidecar` running `cai-workbench-mcp-sidecar`, binds `0.0.0.0:8080`. Env: `WORKBENCH_HOST`, `MCP_UPSTREAM_URL=http://127.0.0.1:8081`, `MCP_OAUTH_ISSUER`, `MCP_OAUTH_JWKS_URL`, `MCP_OAUTH_AUDIENCE`, `MCP_OAUTH_PUBLIC_KEY_PATH`, `MCP_CACHE_TTL_SECONDS`, `KNOX_PROXY_AUTH_ENABLED` (derived from `AWCAuthConfig.EnableAWCAuth`).
  - `mcp-server` running `cai-workbench-mcp-http`, binds `127.0.0.1:8081`. Env: `WORKBENCH_HOST`, `MCP_BIND_HOST=127.0.0.1`, `MCP_BIND_PORT=8081`. Deliberately unreachable outside the pod.
  - `fluent-bit-sidecar` — standard log helper, same as other pods in this chart.
  - Both application containers built from the same image (`cdsw/cai-mcp:{{ .Values.GitSHA }}`) with different `command:` entry points. Both mount the existing `web-tls2` Secret at `/ca/web` so the sidecar can verify OAuth JWTs against the same RSA key pair the web service uses for consoles JWTs. Standard `cdswint` pod-security-context and `capabilities.drop: ["ALL"]`.
  - `Service` (ClusterIP, port 80 → targetPort 8080), selector `role: mcp`.
- `mcp-ingress.yaml` — three-way ingress mirror of [`api-ingress.yaml`](../github.infra.cloudera.com/Sense/cloudera-sense/packaging/chart/cdsw-entrypoints/templates/api-ingress.yaml), chosen at render time by the same flags every other ingress in this chart uses:
  - Istio `VirtualService` (`EnableIstioIngressGateway=true`) for `mcp.<domain>`.
  - GatewayAPI `HTTPRoute + ListenerSet + DNSEndpoint` (`GatewayAPI.Enabled=true`).
  - Standard k8s `Ingress` fallback with TLS from `.Values.PrivateTLSSecret` (or `<secret>-mcp-<ns>` when `ExternalCertificateIssuer.Enable` is set).
- `serviceaccounts.yaml` (modified) — new `ServiceAccount` `{{ .Values.MCP.SAName }}` (default `sa-cdsw-mcp`), gated on `MCP.Enabled`; appended as a subject on the PrivateCloud RoleBinding.
- Values block in [`packaging/chart/cdsw-combined/values.yaml`](../github.infra.cloudera.com/Sense/cloudera-sense/packaging/chart/cdsw-combined/values.yaml) — `MCP.{Enabled, Name, SAName, ServiceName, Port, InternalPort, Replicas, OAuthAudience, CacheTTLSeconds, Resources, TranslationSidecar.Resources}`. `cml-values.yaml` carries a minimal `MCP: Enabled: false` stub so ops can flip the toggle per-environment without redefining the whole block.
- `AuthorizationPolicy` entries live in the sibling `cdsw-istio-security-policies` chart, not in `cdsw-entrypoints`: a new `mcp` policy allows traffic from the Istio ingress gateway namespace + the MCP SA itself; the MCP SA principal is added conditionally to the `api` and `web` policies so the sidecar can reach `/api/v2/auth/exchange`, `/api/v2/auth/validate_key`, and `/oauth/jwks`.

Traffic from the sidecar to APIv2 stays inside the cluster (`http://api.<ns>.svc.cluster.local`). Knox handles TLS termination and, when `KNOX_PROXY_AUTH_ENABLED=true`, trusted-header injection at the ingress — the sidecar honors those headers the same way [`services/web/server/lib/knox-auth.js`](../github.infra.cloudera.com/Sense/cloudera-sense/services/web/server/lib/knox-auth.js) does.

Details of the chart additions are documented in [`packaging/chart/cdsw-entrypoints/README_remote_mcp_addition.md`](../github.infra.cloudera.com/Sense/cloudera-sense/packaging/chart/cdsw-entrypoints/README_remote_mcp_addition.md).

## Files to modify / create

**In this repo (`CAI_Workbench_MCP_Server`):**

| File | Change |
|---|---|
| `cai_workbench_mcp_server/translation_sidecar.py` | **New** — the full sidecar: Starlette app, MCP-spec discovery, token classify/verify/exchange, in-memory cache, httpx reverse proxy |
| `cai_workbench_mcp_server/auth/context.py` | **New** — `request_config` ContextVar + helpers used by `http_server.py` |
| `cai_workbench_mcp_server/http_server.py` | **Modify** — read `X-CAI-Downstream-Bearer`; rewrite `get_config()` to read from ContextVar; refuse requests without the header; bind to `127.0.0.1` by default. Also register the 4 diagnostic tools missing today (`health_check`, `generate_diag_bundle`, `get_diag_bundle_status`, `download_diag_bundle`) |
| `cai_workbench_mcp_server/src/functions/**` | **Unchanged** — `(config, params)` shape and `setup_client(host, api_key)` seam already right |
| `cai_workbench_mcp_server/stdio_server.py` | **Unchanged** — local stdio keeps env-var config |
| `pyproject.toml` | **Update** — add `cai-workbench-mcp-sidecar = "cai_workbench_mcp_server.translation_sidecar:main"` entry point. Deps: `starlette`, `uvicorn`, `httpx`, `pyjwt[crypto]` (all already listed or bundled with FastMCP) |
| `tests/sidecar/` | **New** — unit tests for token classification, verification, cache TTL, header rewriting, discovery endpoints |
| `tests/auth/` | **New** — unit tests for MCP-side ContextVar isolation and `X-CAI-Downstream-Bearer` refusal path |

**In [cloudera-sense](../github.infra.cloudera.com/Sense/cloudera-sense/) — landed in commit `7209d48fdb`:**

| File | Change |
|---|---|
| `services/web/server/api/v1/controllers/oauth/index.js` | **New** — single OAuth 2.1 AS controller: authorize / callback / token / register / jwks / discovery. Reuses `lib/auth.js` `issueAuthToken` machinery, delegates login to the existing SAML/LDAP/Knox stack |
| `services/web/server/lib/oauth-jwks.js` + `.unit.test.js` | **New** — RS256 signing helper + JWKS document builder |
| `services/web/server/db/entities/oauth/{OAuthClient,OAuthAuthorizationCode}.ts` | **New** — DCR client registry + short-lived auth-code storage |
| `services/web/server/db/migrations/20260826120000-oauth-mcp-tables.js` | **New** — migration for the two OAuth tables |
| `services/web/server/db/RepositoryProvider.ts`, `entities/index.ts`, `api/index.js` | **Modify** — register entities + mount `/oauth/*` routes |
| `services/api/proto/mlapiv2/api.proto` | **Modify** — new `ExchangeMcpToken` RPC → `POST /api/v2/auth/exchange` |
| `services/api/srv/auth/exchange.go` + `_test.go` | **New** — verifies the RS256 JWT against the web AS public key at `/ca/web/tls.pub`, resolves the workbench user, mints a short-lived opaque APIv2 key (`hex64.hex64`) via the existing apikeys machinery |
| `services/api/srv/auth/auth.go` | **Modify** — narrow bypass in `Authenticate()` for `/api/v2/auth/exchange` only; handler self-verifies its caller, so credential extraction is skipped and no `ClientAuthData` is populated (documented contract) |
| `services/api/srv/{apikeys,config,impl}/*.go` | **Modify** — plumb the MCP-OAuth public key / issuer / audience config knobs and expose the new endpoint |
| `packaging/chart/cdsw-entrypoints/templates/mcp.yaml` | **New** — three-container `Deployment` (translation-sidecar + mcp-server + fluent-bit-sidecar) + `Service`, gated on `MCP.Enabled` |
| `packaging/chart/cdsw-entrypoints/templates/mcp-ingress.yaml` | **New** — three-way ingress: Istio `VirtualService`, GatewayAPI `HTTPRoute+ListenerSet+DNSEndpoint`, or standard k8s `Ingress` |
| `packaging/chart/cdsw-entrypoints/templates/serviceaccounts.yaml` | **Modify** — new `sa-cdsw-mcp` ServiceAccount + RoleBinding subject |
| `packaging/chart/cdsw-entrypoints/templates/{api,web}.yaml` | **Modify** — touch-ups |
| `packaging/chart/cdsw-combined/values.yaml`, `cml-values.yaml` | **Modify** — `MCP.*` values block |
| `packaging/chart/cdsw-entrypoints/README_remote_mcp_addition.md` | **New** — chart documentation |
| `packaging/chart/cdsw-istio-security-policies/templates/istio-service-authorization-policies.yaml` | **Modify** — new `mcp` policy + MCP SA principal added to `api` and `web` policies |

## Verification

1. **Bearer/JWT path (headless, existing key):**
   - Create a workbench API key via UI (Settings → API keys).
   - `curl -H "Authorization: Bearer $KEY" https://mcp.<workbench-domain>/mcp -X POST -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'` returns the tool list. Sidecar logs the classification (`type=apiv2-key`), cache miss, then a hit on the second call within 60 s.
   - Call `list_project_names` with two different users' keys against the same MCP pod; each response contains only that user's projects (proves multi-tenancy).

2. **MCP OAuth 2.1 path (interactive, discovery-driven):**
   - Point Claude Desktop at `https://mcp.<workbench-domain>/mcp` with no bearer.
   - Expect: 401 + `WWW-Authenticate: Bearer resource_metadata="https://mcp.<workbench-domain>/.well-known/oauth-protected-resource"`.
   - Claude Desktop fetches the metadata, discovers the AS, performs DCR against `/oauth/register` on `services/web`, opens the workbench login page, completes PKCE, reconnects with a Bearer.
   - Sidecar classifies the token, verifies against JWKS, calls `/api/v2/auth/exchange`, forwards to MCP with `X-CAI-Downstream-Bearer`. `list_project_names` works.

2b. **CDP IAM workload auth token path (headless, pre-obtained):**
   - Operator mints a token via `cdp iam generate-workload-auth-token --workload-name DE --profile <env> | jq -r '.token'` and exports it as `$TOKEN`.
   - `curl -H "Authorization: Bearer $TOKEN" https://mcp.<workbench-domain>/mcp -X POST -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'` returns the tool list.
   - Sidecar logs `classified=cdp-iam-workload cache=miss exchange_ok=true principal=<username>`; second call within 60 s: `cache=hit`.
   - Two users with their own IAM tokens against the same MCP pod → each `list_project_names` response contains only that user's projects (multi-tenancy).
   - Token whose `iss` is not in `MCP_IAM_ISSUERS` → sidecar classifies as `apiv2-jwt`, `/validate_key` returns 401, sidecar returns 401 + `WWW-Authenticate` challenge.
   - Deployed with `MCP.IAM.Enabled=false` (default) → IAM tokens are treated as generic APIv2 JWTs and rejected. Confirms the feature is opt-in.

3. **Header-refusal defense in depth:**
   - `kubectl exec` into the MCP container and hit `http://127.0.0.1:8081/mcp` with a raw `Authorization: Bearer <api-key>` (no `X-CAI-Downstream-Bearer`). MCP returns 401 with a log line indicating a missing sidecar header.

4. **Revoked token pass-through:**
   - Delete an API key via the UI while an MCP session is active. Next tool call → sidecar cache entry hits, forwards to APIv2, gets 401 → sidecar evicts the cache line, returns 401 + `WWW-Authenticate` to the client. Client re-authenticates.

5. **Knox trusted-header path:**
   - Deploy behind Knox with `KNOX_PROXY_AUTH_ENABLED=true`.
   - Request with only `x-cdp-actor-crn` (no `Authorization`) → sidecar recognizes the Knox path and JIT-provisions like `knox-auth.js` does; downstream call is made with an internal Knox-issued session.

6. **Unit tests (sidecar):**
   - Token classifier fuzzed on the boundary between `hex64.hex64` and JWT.
   - JWKS verification rejects wrong issuer, wrong audience, expired token.
   - Cache TTL honored; evicted on downstream 401.
   - `Authorization` is stripped on the way out to MCP; `X-CAI-Downstream-Bearer` and `X-CAI-Principal` are set.

7. **Unit tests (MCP):**
   - Missing `X-CAI-Downstream-Bearer` → 401 without hitting any tool.
   - `request_config` never leaks between concurrent requests (asyncio test with two different bearers).

8. **Integration with cmlapi:**
   - `MCP_LOG_LEVEL=DEBUG` — confirm the outbound cmlapi `Authorization` on each request equals `X-CAI-Downstream-Bearer` for that request — not the pod's service-account key.

## Out of scope

- Rewriting `stdio_server.py`. Local escape hatch; leave it alone.
- Per-user workbench API-key vault. Caller's bearer suffices.
- Rate limiting / audit logging. Standard Istio observability applies; MCP-level rate limits can be a follow-up.
- Session-scoped `project_id`. Current per-call `params.project_id` (with fallback) still works when `config.project_id` is None; leave it.
- External cache (Redis/memcached). In-memory dict is sufficient at the target scale (~1000 users).

## Implementation order

1. ✅ **`auth/context.py` + `auth/middleware.py`** + `http_server.py` rewire — read `X-CAI-Downstream-Bearer`, populate ContextVar, refuse missing header. (This commit.)
2. ✅ **`translation_sidecar.py`** — API-key path first: classify → validate_key → forward. Unit tests under `tests/test_translation_sidecar.py` and `tests/test_auth_middleware.py`. (This commit.)
3. Add the 4 missing diagnostic tools; parity with `stdio_server.py`. (Follow-up.)
4. ✅ `services/api/srv/auth/exchange.go` — token-exchange endpoint on APIv2. (`cloudera-sense@7209d48fdb`.)
5. ✅ `services/web/server/api/v1/controllers/oauth/index.js` — OAuth AS routes, discovery, DCR. (`cloudera-sense@7209d48fdb`.)
6. ✅ Helm templates `mcp.yaml` + `mcp-ingress.yaml` + ServiceAccount + AuthorizationPolicy entries. (`cloudera-sense@7209d48fdb`.) — pending deploy + two-key multi-tenancy test.
7. Extend sidecar with OAuth-classification + JWKS + exchange call. Verify with Claude Desktop end to end. (Follow-up.)
