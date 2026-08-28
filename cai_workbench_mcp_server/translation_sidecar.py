"""Translation sidecar for the multi-tenant CAI Workbench MCP server.

The sidecar is the entire authenticated boundary for the MCP pod. It runs
in a second container alongside ``http_server.py`` (both in the same pod,
same image, different entry points) and owns:

- The MCP-spec OAuth 2.1 discovery surface (``/.well-known/oauth-protected-
  resource`` + ``WWW-Authenticate: Bearer resource_metadata=...`` on 401).
- Classification of every inbound ``Authorization: Bearer <token>`` as
  either an APIv2 API key / web JWT (verified via
  ``/api/v2/auth/validate_key`` on the workbench) or a MCP OAuth access
  token (verified against the workbench AS JWKS, then exchanged via
  ``/api/v2/auth/exchange`` for an APIv2-audience token).
- A small in-memory cache keyed by ``sha256(caller-bearer)`` so the same
  client bearer doesn't cost a round-trip on every tool call.
- Header rewriting on the way to MCP: the inbound ``Authorization`` is
  stripped and ``X-CAI-Downstream-Bearer`` / ``X-CAI-Principal`` are
  injected so the MCP server (bound to loopback in the pod) can trust the
  request came through us and pick up the caller's identity.

The sidecar deliberately depends on Starlette + httpx only — no FastMCP —
because it is not an MCP server. It's a reverse proxy that speaks HTTP.

Auth scheme dispatch (PoC)
--------------------------

For proof-of-concept work the sidecar dispatches purely on the ``Authorization``
header's *scheme*, not on token shape or issuer:

- ``Authorization: BearerV2 <token>`` → treat as an APIv2 credential
  (API key or workbench web JWT). Verified via ``/api/v2/auth/validate_key``
  on the workbench and forwarded verbatim as the downstream bearer.
- ``Authorization: Bearer <token>`` → treat as a CDP IAM workload auth
  token. The sidecar does **no** signature verification; it forwards the
  raw JWT to ``/api/v2/auth/exchange`` with ``token_type=cdp_iam_workload``
  and the workbench decodes the ``sub`` claim to mint a short-lived APIv2
  key. Rationale: JWKS fetch for CDP IAM (thunderhead consoleauth)
  requires x-altus-auth request signing that the workbench doesn't have
  provisioned yet; deferring signature verification is the PoC-scope
  compromise. The workbench's user-lookup step still gates access to a
  known workbench identity.

The MCP OAuth 2.1 verification path (``_validate_oauth``) is preserved in
the code but unreachable under the PoC dispatch. When we're ready to
bring proper OAuth back online, either route ``Bearer`` to it (and give
IAM its own scheme) or add a per-token issuer-sniff back in front of the
scheme check.
"""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, FrozenSet, Optional, Tuple

import httpx
import jwt
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

logger = logging.getLogger("cai_workbench_mcp.translation_sidecar")


# --- Header contract shared with cai_workbench_mcp_server.auth.middleware ---
#
# Kept as string literals here to avoid a runtime dependency between the
# sidecar container and the MCP container — they ship in the same image
# today but the sidecar shouldn't need to import from the MCP package.
DOWNSTREAM_BEARER_HEADER = "X-CAI-Downstream-Bearer"
PRINCIPAL_HEADER = "X-CAI-Principal"

# Regex for APIv2 API keys — 64 lowercase hex + "." + 64 lowercase hex.
# Matches services/api/srv/auth/apikeys.GetHash's shape.
_APIV2_KEY_RE = re.compile(r"^[0-9a-f]{64}\.[0-9a-f]{64}$")

# Hop-by-hop headers that must not be forwarded. Streamable HTTP is a
# single logical connection between the client and MCP server, so we let
# httpx / Starlette handle connection framing themselves.
_HOP_BY_HOP = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailer",
        "transfer-encoding",
        "upgrade",
        "host",
        # Auth is rewritten explicitly by _forward().
        "authorization",
        # Never let a client forge these on the way in.
        DOWNSTREAM_BEARER_HEADER.lower(),
        PRINCIPAL_HEADER.lower(),
    }
)


@dataclass(frozen=True)
class CacheEntry:
    """A successfully-validated caller bearer.

    ``downstream_bearer`` is what we hand to MCP via
    ``X-CAI-Downstream-Bearer`` — either the caller's own APIv2 key
    verbatim, or the APIv2-audience JWT we obtained via
    ``/api/v2/auth/exchange`` for an OAuth caller.
    """

    downstream_bearer: str
    principal: Optional[str]
    expires_at: float  # monotonic seconds


class BearerCache:
    """Tiny in-memory cache for validated caller bearers.

    Keyed by ``sha256(caller_bearer)`` so a leaked cache dump doesn't
    reveal the tokens themselves. Sized for the workbench scale (<= ~1000
    users) — a plain dict with a max size and TTL is all we need. If we
    ever outgrow this we can drop a real LRU in without changing callers.
    """

    def __init__(self, max_size: int = 4096) -> None:
        self._store: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._lock = asyncio.Lock()

    @staticmethod
    def _key(bearer: str) -> str:
        return hashlib.sha256(bearer.encode("utf-8")).hexdigest()

    async def get(self, bearer: str) -> Optional[CacheEntry]:
        key = self._key(bearer)
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.expires_at <= time.monotonic():
                # Stale — drop it so a subsequent get() re-validates.
                self._store.pop(key, None)
                return None
            return entry

    async def put(self, bearer: str, entry: CacheEntry) -> None:
        key = self._key(bearer)
        async with self._lock:
            # Bounded size — evict a random entry when full. We don't care
            # about strict LRU semantics; the TTL is short and workloads
            # are far below max_size in practice.
            if len(self._store) >= self._max_size and key not in self._store:
                self._store.pop(next(iter(self._store)), None)
            self._store[key] = entry

    async def invalidate(self, bearer: str) -> None:
        key = self._key(bearer)
        async with self._lock:
            self._store.pop(key, None)


# --- Configuration ---------------------------------------------------------


def _parse_issuer_list(raw: str) -> FrozenSet[str]:
    """Parse a comma-separated issuer list from an env var.

    Whitespace around each entry is stripped; empty entries are dropped.
    Returns an empty frozenset when the env var is unset or contains only
    separators — the caller treats that as "this token path is disabled".
    """
    if not raw:
        return frozenset()
    return frozenset(item.strip() for item in raw.split(",") if item.strip())


@dataclass(frozen=True)
class SidecarConfig:
    """All the knobs the sidecar reads from the environment at startup."""

    workbench_host: str
    mcp_upstream_url: str
    listen_host: str
    listen_port: int
    cache_ttl_seconds: float
    oauth_issuer: Optional[str]
    oauth_jwks_url: Optional[str]
    oauth_audience: str
    # Accepted CDP IAM workload-auth-token issuers. Empty = the CDP IAM
    # path is disabled and tokens with those issuers will fall through to
    # the generic APIv2 JWT path (which will 401 at /validate_key). We
    # accept a set so a single sidecar image can straddle CDP int/dev/prod
    # without a rebuild — the operator lists all issuers the deployment
    # should honor.
    iam_issuers: FrozenSet[str]
    resource_metadata_url: str
    request_timeout_seconds: float

    @classmethod
    def from_env(cls) -> "SidecarConfig":
        workbench_host = os.environ.get("WORKBENCH_HOST", "").rstrip("/")
        if not workbench_host:
            raise RuntimeError(
                "WORKBENCH_HOST is not set. The Helm chart is expected to "
                "inject this at deploy time; for local dev, export it "
                "manually."
            )
        return cls(
            workbench_host=workbench_host,
            mcp_upstream_url=os.environ.get(
                "MCP_UPSTREAM_URL", "http://127.0.0.1:8081"
            ).rstrip("/"),
            listen_host=os.environ.get("LISTEN_HOST", "0.0.0.0"),
            listen_port=int(os.environ.get("LISTEN_PORT", "8080")),
            cache_ttl_seconds=float(os.environ.get("MCP_CACHE_TTL_SECONDS", "60")),
            oauth_issuer=os.environ.get("MCP_OAUTH_ISSUER") or None,
            oauth_jwks_url=os.environ.get("MCP_OAUTH_JWKS_URL") or None,
            oauth_audience=os.environ.get("MCP_OAUTH_AUDIENCE", "cai-workbench-mcp"),
            iam_issuers=_parse_issuer_list(os.environ.get("MCP_IAM_ISSUERS", "")),
            resource_metadata_url=os.environ.get(
                "MCP_RESOURCE_METADATA_URL",
                "/.well-known/oauth-protected-resource",
            ),
            request_timeout_seconds=float(
                os.environ.get("MCP_REQUEST_TIMEOUT_SECONDS", "60")
            ),
        )


# --- Token classification --------------------------------------------------


class TokenKind:
    APIV2_KEY = "apiv2-key"
    APIV2_JWT = "apiv2-jwt"
    MCP_OAUTH = "mcp-oauth"
    CDP_IAM_WORKLOAD = "cdp-iam-workload"
    UNKNOWN = "unknown"


def classify_token(token: str, cfg: SidecarConfig) -> str:
    """Classify a bearer without verifying it.

    Cheap first-pass check that lets us pick the right verification path
    without paying for a JWKS fetch or a workbench round-trip on requests
    that will fail anyway. The result is *not* trusted for authorization
    — every path re-verifies before allowing the request through.

    NOTE: Under the current PoC dispatch (see module docstring) ``_forward``
    picks the token kind from the ``Authorization`` scheme (``BearerV2``
    vs ``Bearer``) and does not call this function. It's kept in place
    because the test suite exercises it and because we'll likely want to
    reintroduce issuer-based classification once full MCP OAuth
    verification is back on.
    """
    if _APIV2_KEY_RE.match(token):
        return TokenKind.APIV2_KEY
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
    except jwt.InvalidTokenError:
        return TokenKind.UNKNOWN

    iss = unverified.get("iss")
    if cfg.oauth_issuer and iss == cfg.oauth_issuer:
        return TokenKind.MCP_OAUTH
    # CDP IAM workload auth tokens are RS256 JWTs minted by Cloudera's
    # central IAM service. Verification is delegated to the workbench (see
    # module docstring); classification here is just an issuer-match so we
    # know to send this token to /exchange with the right discriminator
    # instead of to /validate_key.
    if iss and iss in cfg.iam_issuers:
        return TokenKind.CDP_IAM_WORKLOAD
    # Anything else that looks like a JWT (including the workbench web
    # JWT the browser UI uses) goes through /validate_key just like an
    # API key — that endpoint bypasses the audience check.
    return TokenKind.APIV2_JWT


# --- Verification & exchange ----------------------------------------------


class AuthError(Exception):
    """Raised when a caller bearer cannot be validated.

    The sidecar always converts this to a 401 with the MCP-spec discovery
    challenge — never leaks the underlying reason to the client.
    """


async def _validate_apiv2(
    token: str, cfg: SidecarConfig, client: httpx.AsyncClient
) -> Tuple[str, Optional[str], Optional[float]]:
    """Validate an APIv2 API key or web JWT against the workbench.

    Returns ``(downstream_bearer, principal, expires_at_monotonic)``. The
    downstream bearer for the APIv2 path is the caller's token verbatim.
    ``expires_at_monotonic`` is ``None`` when the workbench doesn't tell
    us — we fall back to the sidecar's cache TTL in that case.
    """
    url = f"{cfg.workbench_host}/api/v2/auth/validate_key"
    # ValidateAPIKeyRequest.audience is proto-validated as
    # `in: ["API", "Application"]` — grpc-gateway rejects an empty body with
    # 400 before the handler ever runs (see services/api/proto/mlapiv2/
    # api.proto ValidateAPIKeyRequest). MCP tools always hit APIv2, so the
    # audience we care about is "API": that both satisfies the proto rule and
    # tells the handler (auth.go ValidateAPIKeyHandler) to enforce the key
    # was minted with the "API" audience, rejecting keys scoped only to
    # "Application" from being used against MCP.
    try:
        resp = await client.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            json={"audience": "API"},
            timeout=cfg.request_timeout_seconds,
        )
    except httpx.HTTPError as exc:
        # Network-level failure — treat as upstream unavailable, not as an
        # auth failure. The dispatcher converts this to a 502.
        raise UpstreamError(str(exc)) from exc

    if resp.status_code == 401:
        raise AuthError("workbench rejected the bearer")
    if resp.status_code >= 500:
        raise UpstreamError(f"validate_key returned {resp.status_code}")
    if resp.status_code != 200:
        raise AuthError(f"validate_key returned {resp.status_code}")

    body: Dict[str, Any] = {}
    try:
        body = resp.json() or {}
    except ValueError:
        # Empty body / non-JSON — the endpoint still 200'd, so treat the
        # bearer as valid with no attached principal.
        pass

    principal = (
        body.get("username")
        or body.get("subject")
        or body.get("sub")
        or None
    )
    return token, principal, None


async def _validate_oauth(
    token: str, cfg: SidecarConfig, client: httpx.AsyncClient
) -> Tuple[str, Optional[str], Optional[float]]:
    """Verify a MCP OAuth access token and exchange it for an APIv2 token.

    Signature verification uses the workbench AS JWKS. On success we hit
    ``/api/v2/auth/exchange`` on APIv2, which lives in the cloudera-sense
    repo (see ``services/api/srv/auth/exchange.go`` in the plan), to get
    back an ``aud=API`` short-lived JWT bound to the same subject.

    This branch is a working skeleton — the JWKS verification path is
    exercised end-to-end by tests, but production use requires the
    cloudera-sense side to be deployed. Until then, any OAuth caller will
    get a 502 with a clear "exchange endpoint unavailable" log line.
    """
    if not cfg.oauth_jwks_url or not cfg.oauth_issuer:
        raise AuthError("OAuth path not configured on this sidecar")

    # Verify signature + iss + aud against the workbench AS. We fetch the
    # JWKS lazily and let PyJWKClient cache it internally.
    jwks_client = _get_jwks_client(cfg.oauth_jwks_url)
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256", "ES256"],
            issuer=cfg.oauth_issuer,
            audience=cfg.oauth_audience,
        )
    except jwt.InvalidTokenError as exc:
        raise AuthError(f"OAuth token verification failed: {exc}") from exc

    principal = claims.get("sub") or claims.get("username")

    downstream, exchange_principal, expires_at = await _call_exchange(
        token,
        token_type="mcp_oauth",
        cfg=cfg,
        client=client,
    )
    # Prefer the principal the workbench returned (authoritative), but
    # fall back to the JWT's own sub/username claim if the response omitted
    # username.
    return downstream, exchange_principal or principal, expires_at


async def _exchange_iam_workload(
    token: str, cfg: SidecarConfig, client: httpx.AsyncClient
) -> Tuple[str, Optional[str], Optional[float]]:
    """Exchange a CDP IAM workload auth token for an APIv2 downstream key.

    The sidecar does no signature verification on this branch — the
    workbench's ``/api/v2/auth/exchange`` handler owns that boundary (it
    holds the CDP IAM JWKS URL / issuer / audience config). Our job is
    just to classify the token (already done by the caller via
    ``classify_token``) and hand it off with the right discriminator.

    Returns the same ``(downstream_bearer, principal, expires_at)`` triple
    as the other verify helpers so the caching layer treats it uniformly.
    """
    return await _call_exchange(
        token,
        token_type="cdp_iam_workload",
        cfg=cfg,
        client=client,
    )


async def _call_exchange(
    token: str,
    *,
    token_type: str,
    cfg: SidecarConfig,
    client: httpx.AsyncClient,
) -> Tuple[str, Optional[str], Optional[float]]:
    """POST to ``/api/v2/auth/exchange`` and interpret the response.

    Wire contract with the cloudera-sense handler in
    services/api/srv/auth/exchange.go — see the proto in
    services/api/proto/mlapiv2/api.proto (ExchangeMcpTokenRequest /
    ExchangeMcpTokenResponse). The endpoint is a gRPC-gateway REST
    projection, so it reads ``token`` (and the new optional ``token_type``
    discriminator) from the JSON body — never from the Authorization
    header. The interceptor bypass covers this path but the handler itself
    binds off the request message.

    Response shape per the proto: ``api_key`` (opaque plaintext APIv2 key
    in "hex64.hex64" form), ``expires_at`` (absolute unix seconds), and
    ``username``. ``access_token`` / ``expires_in`` are honored as
    backward-compatible aliases in case a future variant of the handler
    ever renames these to OAuth-flavored keys.
    """
    url = f"{cfg.workbench_host}/api/v2/auth/exchange"
    body: Dict[str, Any] = {"token": token}
    # ``token_type`` is optional server-side; omit it when empty so we
    # stay compatible with an older workbench build that hasn't picked up
    # the new proto field yet.
    if token_type:
        body["token_type"] = token_type
    try:
        resp = await client.post(
            url,
            json=body,
            timeout=cfg.request_timeout_seconds,
        )
    except httpx.HTTPError as exc:
        raise UpstreamError(str(exc)) from exc

    if resp.status_code == 404:
        # The endpoint isn't deployed yet in this cloudera-sense build.
        # Convert to an upstream error rather than pretending the caller
        # is invalid — the operator needs to know the wiring is missing.
        raise UpstreamError("/api/v2/auth/exchange not available on workbench")
    if resp.status_code == 401:
        raise AuthError(f"workbench refused to exchange the {token_type or 'mcp_oauth'} token")
    if resp.status_code == 412:
        # FailedPrecondition — the workbench recognizes the token_type but
        # doesn't have the config plumbed to verify it (e.g. no
        # CDPIAMJWKSURL for a cdp_iam_workload request). Not a caller
        # error; surface it as an upstream problem.
        raise UpstreamError(f"workbench not configured for token_type={token_type!r}")
    if resp.status_code >= 500:
        raise UpstreamError(f"exchange returned {resp.status_code}")
    if resp.status_code != 200:
        raise AuthError(f"exchange returned {resp.status_code}")

    payload = resp.json()
    downstream = (
        payload.get("api_key")
        or payload.get("access_token")
        or payload.get("token")
    )
    if not downstream:
        raise UpstreamError("exchange response missing api_key")
    principal = payload.get("username") or payload.get("sub") or None
    expires_at_unix = payload.get("expires_at")
    expires_in = payload.get("expires_in")
    if expires_at_unix is not None:
        # ``expires_at`` is wall-clock unix seconds. Convert to a monotonic
        # deadline so the cache TTL logic stays clock-skew safe.
        remaining = float(expires_at_unix) - time.time()
        expires_at = time.monotonic() + max(remaining, 0.0)
    elif expires_in is not None:
        expires_at = time.monotonic() + float(expires_in)
    else:
        expires_at = None
    return downstream, principal, expires_at


_JWKS_CLIENTS: Dict[str, "jwt.PyJWKClient"] = {}


def _get_jwks_client(url: str) -> "jwt.PyJWKClient":
    """Memoize PyJWKClient by URL so JWKS caching survives across requests."""
    client = _JWKS_CLIENTS.get(url)
    if client is None:
        client = jwt.PyJWKClient(url)
        _JWKS_CLIENTS[url] = client
    return client


class UpstreamError(Exception):
    """Raised when the workbench APIv2 is unreachable / broken.

    Converted to 502 for the client; unlike :class:`AuthError` this does
    not carry the MCP-spec discovery challenge because retrying with a new
    bearer won't help.
    """


# --- Reverse proxy ---------------------------------------------------------


def _public_base_url(request: Request) -> str:
    """Return the client-facing scheme+host for this request.

    Istio terminates TLS at the ingress gateway and forwards to the pod
    over plain HTTP, so ``request.url.scheme`` inside the sidecar is
    ``http`` even when the caller reached us at ``https://``. If we echo
    that scheme back in discovery metadata (``resource``, WWW-Authenticate
    ``resource_metadata=``) strict OAuth 2.1 clients reject the mismatch
    against the URL they actually called.

    We honor ``X-Forwarded-Proto`` (set by Istio's envoy) and
    ``X-Forwarded-Host`` when present, and fall back to the request's own
    view otherwise. This is safe because the sidecar sits behind the
    cluster ingress; a caller cannot reach us without those headers going
    through envoy.
    """
    scheme = request.headers.get("x-forwarded-proto")
    if scheme:
        # A comma-separated list means multiple hops — take the first,
        # which is closest to the original client.
        scheme = scheme.split(",", 1)[0].strip()
    if not scheme:
        scheme = request.url.scheme
    host = request.headers.get("x-forwarded-host")
    if host:
        host = host.split(",", 1)[0].strip()
    if not host:
        host = request.url.netloc
    return f"{scheme}://{host}"


def _www_authenticate(request: Request) -> str:
    """Build the MCP-spec ``WWW-Authenticate`` challenge value.

    Uses the request's own scheme+host so the metadata URL is reachable
    from the client's perspective — important behind Istio / Knox where
    the pod itself doesn't know its public hostname.
    """
    cfg: SidecarConfig = request.app.state.cfg
    base = _public_base_url(request)
    return f'Bearer resource_metadata="{base}{cfg.resource_metadata_url}"'


def _challenge_response(
    request: Request, status_code: int = 401, detail: str = "authentication required"
) -> JSONResponse:
    return JSONResponse(
        {"error": "unauthorized", "detail": detail},
        status_code=status_code,
        headers={"WWW-Authenticate": _www_authenticate(request)},
    )


async def oauth_protected_resource(request: Request) -> JSONResponse:
    """RFC 9728 Protected Resource Metadata for MCP client discovery.

    Reachable at two path shapes:

    - ``/.well-known/oauth-protected-resource`` — resource metadata for
      the whole sidecar. ``resource`` echoes the base URL.
    - ``/.well-known/oauth-protected-resource/<resource-path>`` — path-
      scoped metadata (MCP spec 2025-06). ``resource`` echoes the base
      plus the suffix (e.g. ``https://mcp.example.com/mcp``). MCP
      Inspector and other spec-compliant clients hit this shape after
      receiving a 401 from ``/mcp`` and use it to locate the AS.

    Both shapes must be publicly accessible — this is discovery metadata,
    not a protected resource. Enforcing auth here would prevent a
    first-contact client from ever learning where to authenticate.
    """
    cfg: SidecarConfig = request.app.state.cfg
    base = _public_base_url(request)
    resource_path = request.path_params.get("resource_path", "") or ""
    # ``resource_path`` from Starlette's path converter never carries a
    # leading slash; add one so we form a valid absolute URL. An empty
    # suffix (the un-scoped variant) leaves ``resource`` at the base.
    if resource_path:
        resource = f"{base}/{resource_path.lstrip('/')}"
    else:
        resource = base
    body = {
        "resource": resource,
        "authorization_servers": [cfg.oauth_issuer] if cfg.oauth_issuer else [],
        "bearer_methods_supported": ["header"],
        "resource_documentation": (
            "Cloudera AI Workbench MCP server. Send Authorization: Bearer "
            "with either an APIv2 API key (hex64.hex64), an APIv2 web JWT, "
            "or an OAuth 2.1 access token issued by the workbench AS."
        ),
    }
    return JSONResponse(body)


async def _validate_and_cache(
    token: str,
    kind: str,
    cfg: SidecarConfig,
    cache: BearerCache,
    client: httpx.AsyncClient,
) -> CacheEntry:
    """Return a cache entry for ``token``, validating if necessary.

    ``kind`` is chosen by the caller from the ``Authorization`` scheme
    (see ``_forward``): ``BearerV2`` → APIv2, ``Bearer`` → CDP IAM. The
    classifier is intentionally out of the loop under the PoC dispatch —
    we trust the client to pick the right scheme.
    """
    cached = await cache.get(token)
    if cached is not None:
        return cached

    if kind == TokenKind.APIV2_KEY or kind == TokenKind.APIV2_JWT:
        downstream, principal, expires_at = await _validate_apiv2(token, cfg, client)
    elif kind == TokenKind.MCP_OAUTH:
        downstream, principal, expires_at = await _validate_oauth(token, cfg, client)
    elif kind == TokenKind.CDP_IAM_WORKLOAD:
        # Verification lives on the workbench for this path; the sidecar
        # just forwards with the discriminator set. See
        # _exchange_iam_workload for rationale.
        downstream, principal, expires_at = await _exchange_iam_workload(token, cfg, client)
    else:
        raise AuthError(f"unrecognized token shape: {kind}")

    # Effective TTL: shorter of the caller's remaining token lifetime and
    # the sidecar's cache TTL. The intent is that a revoked token stops
    # working within ``cache_ttl_seconds`` at worst.
    now = time.monotonic()
    expiry = now + cfg.cache_ttl_seconds
    if expires_at is not None:
        expiry = min(expiry, expires_at)
    entry = CacheEntry(downstream_bearer=downstream, principal=principal, expires_at=expiry)
    await cache.put(token, entry)
    return entry


def _prepare_forward_headers(request: Request, entry: CacheEntry) -> Dict[str, str]:
    """Rewrite headers on the way to MCP.

    - Strip ``Authorization`` and any client-supplied MCP-internal
      headers (``X-CAI-*``).
    - Strip hop-by-hop headers.
    - Inject ``X-CAI-Downstream-Bearer`` (authoritative) and
      ``X-CAI-Principal`` (informational).
    """
    out: Dict[str, str] = {}
    for name, value in request.headers.items():
        if name.lower() in _HOP_BY_HOP:
            continue
        if name.lower().startswith("x-cai-"):
            # Never trust a client-forged X-CAI-* header.
            continue
        out[name] = value
    out[DOWNSTREAM_BEARER_HEADER] = entry.downstream_bearer
    if entry.principal:
        out[PRINCIPAL_HEADER] = entry.principal
    return out


async def _forward(request: Request) -> Response:
    """Validate, rewrite headers, and reverse-proxy to the MCP server.

    Streamable HTTP means we can see two request shapes on the same path:
    - a short JSON-RPC POST (single response body), and
    - a long-lived SSE GET (streamed response).

    ``httpx.AsyncClient.stream()`` handles both transparently: we get an
    async iterator over the response bytes and hand it straight to
    :class:`StreamingResponse`. No JSON parsing, no re-framing.
    """
    cfg: SidecarConfig = request.app.state.cfg
    cache: BearerCache = request.app.state.cache
    client: httpx.AsyncClient = request.app.state.http

    auth_header = request.headers.get("authorization", "")
    # PoC dispatch on scheme:
    #   BearerV2 <token>  → APIv2 credential (validate_key path)
    #   Bearer   <token>  → CDP IAM workload token (exchange path)
    # Case-insensitive on the scheme name; the value after is used verbatim.
    scheme_lower = auth_header.split(" ", 1)[0].lower() if auth_header else ""
    if scheme_lower == "bearerv2":
        kind = TokenKind.APIV2_JWT
    elif scheme_lower == "bearer":
        kind = TokenKind.CDP_IAM_WORKLOAD
    else:
        return _challenge_response(request, detail="missing bearer token")

    parts = auth_header.split(" ", 1)
    token = parts[1].strip() if len(parts) == 2 else ""
    if not token:
        return _challenge_response(request, detail="empty bearer token")

    try:
        entry = await _validate_and_cache(token, kind, cfg, cache, client)
    except AuthError as exc:
        logger.info("auth failure: %s", exc)
        return _challenge_response(request, detail="invalid bearer token")
    except UpstreamError as exc:
        logger.warning("upstream failure during auth: %s", exc)
        return JSONResponse(
            {"error": "upstream_unavailable", "detail": "auth backend unavailable"},
            status_code=502,
        )

    headers = _prepare_forward_headers(request, entry)
    upstream_url = f"{cfg.mcp_upstream_url}{request.url.path}"
    if request.url.query:
        upstream_url += f"?{request.url.query}"

    # Read the body once. For SSE GETs the body is empty; for JSON-RPC
    # POSTs it's small (bounded by MCP client policy). We don't need to
    # stream request bodies today.
    body_bytes = await request.body()

    try:
        # ``stream()`` opens the connection but keeps the response body
        # available for streaming; we close it inside the generator.
        upstream_request = client.build_request(
            request.method,
            upstream_url,
            headers=headers,
            content=body_bytes if body_bytes else None,
        )
        upstream_response = await client.send(upstream_request, stream=True)
    except httpx.HTTPError as exc:
        logger.warning("upstream connect failure: %s", exc)
        return JSONResponse(
            {"error": "upstream_unavailable", "detail": "MCP server unreachable"},
            status_code=502,
        )

    if upstream_response.status_code == 401:
        # The MCP server refused despite our validated bearer — most likely
        # the caller's downstream token was revoked between validation and
        # dispatch. Evict the cache line so the next request re-verifies,
        # and return the MCP-spec challenge to the client.
        await cache.invalidate(token)
        await upstream_response.aclose()
        return _challenge_response(request, detail="downstream authorization failed")

    async def body_stream():
        try:
            # ``httpx.MockTransport`` (used in unit tests) hands us a
            # pre-buffered response whose stream is already marked
            # consumed, so ``aiter_raw()`` would raise. Real transports
            # give us a live stream we iterate chunk-by-chunk — critical
            # for MCP's SSE long-poll.
            if upstream_response.is_stream_consumed:
                yield upstream_response.content
            else:
                async for chunk in upstream_response.aiter_raw():
                    yield chunk
        finally:
            await upstream_response.aclose()

    # Filter hop-by-hop headers back out on the response path too.
    response_headers = {
        k: v
        for k, v in upstream_response.headers.items()
        if k.lower() not in _HOP_BY_HOP
    }

    return StreamingResponse(
        body_stream(),
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )


# --- Application factory ---------------------------------------------------


def create_app(cfg: Optional[SidecarConfig] = None) -> Starlette:
    """Build the Starlette ASGI app.

    Kept as a factory so tests can inject a config that points at a fake
    upstream and a controllable JWKS URL.
    """
    resolved = cfg or SidecarConfig.from_env()
    cache = BearerCache()

    @contextlib.asynccontextmanager
    async def _lifespan(app: Starlette) -> AsyncIterator[None]:
        # Reuse a single httpx client for the process lifetime so we
        # benefit from connection pooling to the workbench and the MCP
        # loopback.
        async with httpx.AsyncClient(timeout=resolved.request_timeout_seconds) as http:
            app.state.http = http
            app.state.cfg = resolved
            app.state.cache = cache
            yield

    # Every non-discovery path goes through _forward(). The two discovery
    # routes must precede the fallback — Starlette matches in order.
    #
    # We register the un-scoped path first and the path-scoped variant
    # second so both /.well-known/oauth-protected-resource and
    # /.well-known/oauth-protected-resource/<anything> reach the metadata
    # handler instead of falling through to _forward() (which would
    # 401 first-contact clients before they can discover the AS — this
    # was the exact regression MCP Inspector hit in the field).
    metadata_prefix = resolved.resource_metadata_url.rstrip("/")
    routes = [
        Route(metadata_prefix, oauth_protected_resource, methods=["GET"]),
        Route(
            f"{metadata_prefix}/{{resource_path:path}}",
            oauth_protected_resource,
            methods=["GET"],
        ),
        # Fallback — matches any method, any path. Starlette routes match
        # in order, so this must come last.
        Route("/{full_path:path}", _forward, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]),
    ]

    app = Starlette(routes=routes, lifespan=_lifespan, middleware=[])
    # Attach eagerly for tests that don't drive lifespan.
    app.state.cfg = resolved
    app.state.cache = cache
    return app


def main() -> None:
    """Entry point registered as ``cai-workbench-mcp-sidecar``."""
    import uvicorn

    logging.basicConfig(
        level=os.environ.get("MCP_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    cfg = SidecarConfig.from_env()
    logger.info(
        "starting translation sidecar: listen=%s:%d workbench=%s upstream=%s",
        cfg.listen_host,
        cfg.listen_port,
        cfg.workbench_host,
        cfg.mcp_upstream_url,
    )
    app = create_app(cfg)
    uvicorn.run(app, host=cfg.listen_host, port=cfg.listen_port, log_config=None)


if __name__ == "__main__":
    main()
