"""Unit tests for the translation sidecar.

These tests drive the Starlette app in-process via httpx's ASGI transport.
The workbench APIv2 is mocked with ``respx`` so we can assert exact
outbound calls without spinning up a real server. The upstream MCP server
(where the sidecar would normally forward) is replaced with a small
in-memory recorder that lets us verify:

- the caller's ``Authorization`` header is stripped,
- ``X-CAI-Downstream-Bearer`` is injected with the right token,
- ``X-CAI-Principal`` follows through,
- the cache short-circuits repeated validation.
"""

from __future__ import annotations

import asyncio
import base64
import json
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx
import pytest

from cai_workbench_mcp_server import translation_sidecar as ts


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _cfg(**overrides: Any) -> ts.SidecarConfig:
    """Build a config that never touches the real environment."""
    base = dict(
        workbench_host="http://workbench.test",
        mcp_upstream_url="http://mcp.test",
        listen_host="127.0.0.1",
        listen_port=8080,
        cache_ttl_seconds=60.0,
        oauth_issuer=None,
        oauth_jwks_url=None,
        oauth_audience="cai-workbench-mcp",
        iam_issuers=frozenset(),
        resource_metadata_url="/.well-known/oauth-protected-resource",
        request_timeout_seconds=5.0,
    )
    base.update(overrides)
    return ts.SidecarConfig(**base)


def _fake_jwt(payload: Dict[str, Any]) -> str:
    """Cheap unsigned JWT for classification tests only."""

    def b64(v: Dict[str, Any]) -> str:
        raw = json.dumps(v, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    header = b64({"alg": "none", "typ": "JWT"})
    body = b64(payload)
    return f"{header}.{body}.sig"


class _FakeUpstream:
    """Records every request the sidecar forwards to it."""

    def __init__(
        self,
        status_code: int = 200,
        body: bytes = b'{"ok":true}',
        content_type: str = "application/json",
    ) -> None:
        self.status_code = status_code
        self.body = body
        self.content_type = content_type
        self.requests: List[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(
            status_code=self.status_code,
            content=self.body,
            headers={"content-type": self.content_type},
        )


class _FakeWorkbench:
    """Configurable APIv2 ``/validate_key`` + ``/exchange`` responder.

    Two request buckets so tests can assert exactly which endpoint the
    sidecar hit — ``validate_key`` for APIv2 keys / web JWTs, ``exchange``
    for MCP OAuth and (new) CDP IAM workload tokens.
    """

    def __init__(self) -> None:
        self.calls: List[httpx.Request] = []
        self.exchange_calls: List[httpx.Request] = []
        self.status_code = 200
        self.body: Dict[str, Any] = {"username": "alice"}
        # /exchange defaults (only used when a test hits that path).
        self.exchange_status = 200
        self.exchange_body: Dict[str, Any] = {
            "api_key": "e" * 64 + "." + "f" * 64,
            "expires_at": int(time.time()) + 600,
            "username": "alice",
        }

    def set(self, *, status_code: int = 200, body: Optional[Dict[str, Any]] = None) -> None:
        self.status_code = status_code
        self.body = body if body is not None else self.body

    def set_exchange(
        self,
        *,
        status_code: int = 200,
        body: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.exchange_status = status_code
        if body is not None:
            self.exchange_body = body

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v2/auth/exchange":
            self.exchange_calls.append(request)
            return httpx.Response(status_code=self.exchange_status, json=self.exchange_body)
        self.calls.append(request)
        return httpx.Response(status_code=self.status_code, json=self.body)


def _build_app(
    cfg: ts.SidecarConfig,
    upstream: _FakeUpstream,
    workbench: _FakeWorkbench,
) -> ts.Starlette:
    """Compose a Starlette app whose httpx client is wired to fakes.

    We can't use the real ``lifespan`` (it opens a live httpx client that
    would try to reach real hosts), so we build the routes ourselves and
    attach a client backed by an ``httpx.MockTransport``.
    """
    app = ts.create_app(cfg)

    def dispatch(request: httpx.Request) -> httpx.Response:
        host = request.url.host
        # validate_key / exchange live on the workbench; anything else is
        # a forward to the MCP upstream.
        if request.url.path.startswith("/api/v2/auth/"):
            return workbench.handler(request)
        return upstream.handler(request)

    transport = httpx.MockTransport(dispatch)
    app.state.http = httpx.AsyncClient(transport=transport)
    app.state.cfg = cfg
    app.state.cache = ts.BearerCache()
    return app


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def test_classify_apiv2_key_shape():
    cfg = _cfg()
    token = "a" * 64 + "." + "b" * 64
    assert ts.classify_token(token, cfg) == ts.TokenKind.APIV2_KEY


def test_classify_apiv2_key_rejects_wrong_length():
    cfg = _cfg()
    # 63 hex on the left half — not an APIv2 key. Also not a JWT.
    assert ts.classify_token("a" * 63 + "." + "b" * 64, cfg) == ts.TokenKind.UNKNOWN


def test_classify_apiv2_key_rejects_non_hex():
    cfg = _cfg()
    # Correct shape, but 'g' isn't hex.
    assert ts.classify_token("g" * 64 + "." + "b" * 64, cfg) == ts.TokenKind.UNKNOWN


def test_classify_web_jwt_falls_through_to_apiv2_jwt():
    """A workbench web JWT has no matching OAuth issuer → APIV2_JWT path."""
    cfg = _cfg(oauth_issuer="https://as.workbench.test/")
    token = _fake_jwt({"iss": "https://workbench.test/", "sub": "alice"})
    assert ts.classify_token(token, cfg) == ts.TokenKind.APIV2_JWT


def test_classify_mcp_oauth_when_issuer_matches():
    cfg = _cfg(oauth_issuer="https://as.workbench.test/")
    token = _fake_jwt({"iss": "https://as.workbench.test/", "sub": "alice"})
    assert ts.classify_token(token, cfg) == ts.TokenKind.MCP_OAUTH


def test_classify_garbage_is_unknown():
    cfg = _cfg()
    assert ts.classify_token("hello there", cfg) == ts.TokenKind.UNKNOWN


def test_classify_cdp_iam_workload_when_issuer_matches():
    """A JWT whose ``iss`` is in ``iam_issuers`` classifies as CDP_IAM_WORKLOAD.

    We do NOT verify the signature here — the sidecar delegates that to the
    workbench's ``/api/v2/auth/exchange`` handler. Classification is a
    dispatch cue only.
    """
    iam_iss = "iamapi.us-west-1.altus.cloudera.com"
    cfg = _cfg(iam_issuers=frozenset({iam_iss}))
    token = _fake_jwt({"iss": iam_iss, "sub": "alice"})
    assert ts.classify_token(token, cfg) == ts.TokenKind.CDP_IAM_WORKLOAD


def test_classify_cdp_iam_workload_disabled_when_issuer_not_configured():
    """Empty ``iam_issuers`` = feature off; token falls through to APIV2_JWT."""
    cfg = _cfg(iam_issuers=frozenset())
    token = _fake_jwt(
        {"iss": "iamapi.us-west-1.altus.cloudera.com", "sub": "alice"}
    )
    # No configured IAM issuers → it's just an opaque foreign JWT to us, and
    # the classifier hands it to the /validate_key path which will 401.
    assert ts.classify_token(token, cfg) == ts.TokenKind.APIV2_JWT


def test_classify_mcp_oauth_wins_over_iam_when_both_configured():
    """OAuth issuer match takes precedence over the IAM issuer list.

    They should never overlap in practice, but if a deployment ever lists
    the workbench's own OAuth issuer in ``MCP_IAM_ISSUERS`` we still want
    the OAuth branch (which does JWKS verification) to run.
    """
    same = "https://as.workbench.test/"
    cfg = _cfg(oauth_issuer=same, iam_issuers=frozenset({same}))
    token = _fake_jwt({"iss": same, "sub": "alice"})
    assert ts.classify_token(token, cfg) == ts.TokenKind.MCP_OAUTH


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cache_returns_stored_entry_before_expiry():
    cache = ts.BearerCache()
    entry = ts.CacheEntry(
        downstream_bearer="dwn", principal="alice", expires_at=time.monotonic() + 60
    )
    await cache.put("bearer", entry)
    got = await cache.get("bearer")
    assert got is entry


@pytest.mark.asyncio
async def test_cache_drops_expired_entry():
    cache = ts.BearerCache()
    entry = ts.CacheEntry(
        downstream_bearer="dwn", principal="alice", expires_at=time.monotonic() - 1
    )
    await cache.put("bearer", entry)
    assert await cache.get("bearer") is None


@pytest.mark.asyncio
async def test_cache_invalidate_removes_entry():
    cache = ts.BearerCache()
    entry = ts.CacheEntry(
        downstream_bearer="dwn", principal="alice", expires_at=time.monotonic() + 60
    )
    await cache.put("bearer", entry)
    await cache.invalidate("bearer")
    assert await cache.get("bearer") is None


@pytest.mark.asyncio
async def test_cache_bounded_eviction():
    """When the cache is full a subsequent insert evicts an existing entry."""
    cache = ts.BearerCache(max_size=2)
    await cache.put("a", ts.CacheEntry("da", None, time.monotonic() + 60))
    await cache.put("b", ts.CacheEntry("db", None, time.monotonic() + 60))
    await cache.put("c", ts.CacheEntry("dc", None, time.monotonic() + 60))
    remaining = 0
    for k in ("a", "b", "c"):
        if await cache.get(k) is not None:
            remaining += 1
    assert remaining == 2


# ---------------------------------------------------------------------------
# End-to-end via ASGI transport
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_missing_bearer_returns_401_with_challenge():
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    app = _build_app(_cfg(), upstream, workbench)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        resp = await client.post("/mcp", json={"jsonrpc": "2.0"})
    assert resp.status_code == 401
    challenge = resp.headers.get("www-authenticate", "")
    assert "resource_metadata=" in challenge
    # Upstream must not have been touched.
    assert upstream.requests == []
    assert workbench.calls == []


@pytest.mark.asyncio
async def test_apiv2_key_validates_and_forwards():
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    workbench.set(body={"username": "alice"})
    app = _build_app(_cfg(), upstream, workbench)

    key = "a" * 64 + "." + "b" * 64
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        resp = await client.post(
            "/mcp",
            # BearerV2 → APIv2 path under the PoC scheme dispatch.
            headers={"authorization": f"BearerV2 {key}"},
            json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        )

    assert resp.status_code == 200

    # Workbench validate_key was called exactly once with the caller's key.
    # Outbound to the workbench uses standard `Bearer` — the `BearerV2`
    # scheme is a sidecar-inbound convention only.
    assert len(workbench.calls) == 1
    assert workbench.calls[0].url.path == "/api/v2/auth/validate_key"
    assert workbench.calls[0].headers["authorization"] == f"Bearer {key}"

    # Upstream forward: Authorization stripped, downstream header set.
    assert len(upstream.requests) == 1
    fwd = upstream.requests[0]
    assert "authorization" not in {h.lower() for h in fwd.headers.keys()}
    assert fwd.headers[ts.DOWNSTREAM_BEARER_HEADER] == key
    assert fwd.headers[ts.PRINCIPAL_HEADER] == "alice"


@pytest.mark.asyncio
async def test_workbench_rejection_returns_401():
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    workbench.set(status_code=401, body={})
    app = _build_app(_cfg(), upstream, workbench)

    key = "a" * 64 + "." + "b" * 64
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        resp = await client.post(
            "/mcp",
            headers={"authorization": f"BearerV2 {key}"},
            json={},
        )
    assert resp.status_code == 401
    assert "resource_metadata=" in resp.headers["www-authenticate"]
    # Upstream never touched.
    assert upstream.requests == []


@pytest.mark.asyncio
async def test_cache_short_circuits_second_call():
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    app = _build_app(_cfg(), upstream, workbench)

    key = "a" * 64 + "." + "b" * 64
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        r1 = await client.post("/mcp", headers={"authorization": f"BearerV2 {key}"}, json={})
        r2 = await client.post("/mcp", headers={"authorization": f"BearerV2 {key}"}, json={})

    assert r1.status_code == 200
    assert r2.status_code == 200
    # Workbench validate_key was hit exactly once — the second call was cached.
    assert len(workbench.calls) == 1
    # But both requests were forwarded to MCP upstream.
    assert len(upstream.requests) == 2


@pytest.mark.asyncio
async def test_downstream_401_invalidates_cache():
    upstream = _FakeUpstream(status_code=401)
    workbench = _FakeWorkbench()
    app = _build_app(_cfg(), upstream, workbench)

    key = "a" * 64 + "." + "b" * 64
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        r1 = await client.post("/mcp", headers={"authorization": f"BearerV2 {key}"}, json={})
        # After a downstream 401 the cache line should have been evicted, so
        # the second call re-validates against the workbench.
        r2 = await client.post("/mcp", headers={"authorization": f"BearerV2 {key}"}, json={})

    assert r1.status_code == 401
    assert r2.status_code == 401
    assert len(workbench.calls) == 2


@pytest.mark.asyncio
async def test_cdp_iam_workload_exchanges_and_forwards():
    """A CDP IAM workload JWT goes through /exchange, not /validate_key.

    The sidecar must:
      1. Skip /validate_key entirely (workbench sees no call there).
      2. POST the raw token to /exchange with ``token_type=cdp_iam_workload``.
      3. NOT forward the caller's Authorization header to /exchange
         (the interceptor bypass reads the token from the body).
      4. Inject the exchanged APIv2 key + principal into the upstream
         forward.
    """
    iam_iss = "iamapi.us-west-1.altus.cloudera.com"
    downstream_key = "e" * 64 + "." + "f" * 64
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    workbench.set_exchange(
        body={
            "api_key": downstream_key,
            "expires_at": int(time.time()) + 600,
            "username": "bob",
        }
    )
    app = _build_app(_cfg(iam_issuers=frozenset({iam_iss})), upstream, workbench)

    token = _fake_jwt({"iss": iam_iss, "sub": "bob"})
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        resp = await client.post(
            "/mcp",
            headers={"authorization": f"Bearer {token}"},
            json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        )

    assert resp.status_code == 200

    # validate_key must NOT have been called.
    assert workbench.calls == []

    # /exchange was hit exactly once with the right body.
    assert len(workbench.exchange_calls) == 1
    ex = workbench.exchange_calls[0]
    body = json.loads(ex.content)
    assert body["token"] == token
    assert body["token_type"] == "cdp_iam_workload"
    # No Authorization forwarded on the /exchange call — the endpoint
    # bypasses the auth interceptor and reads the token from the body.
    assert "authorization" not in {h.lower() for h in ex.headers.keys()}

    # Forward: caller's bearer stripped, downstream key + principal injected.
    assert len(upstream.requests) == 1
    fwd = upstream.requests[0]
    assert "authorization" not in {h.lower() for h in fwd.headers.keys()}
    assert fwd.headers[ts.DOWNSTREAM_BEARER_HEADER] == downstream_key
    assert fwd.headers[ts.PRINCIPAL_HEADER] == "bob"


@pytest.mark.asyncio
async def test_cdp_iam_workload_401_returns_401_with_challenge():
    """Workbench rejection of an IAM token surfaces as an MCP-spec 401."""
    iam_iss = "iamapi.us-west-1.altus.cloudera.com"
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    workbench.set_exchange(status_code=401, body={})
    app = _build_app(_cfg(iam_issuers=frozenset({iam_iss})), upstream, workbench)

    token = _fake_jwt({"iss": iam_iss, "sub": "bob"})
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        resp = await client.post(
            "/mcp",
            headers={"authorization": f"Bearer {token}"},
            json={},
        )
    assert resp.status_code == 401
    assert "resource_metadata=" in resp.headers["www-authenticate"]
    assert upstream.requests == []


@pytest.mark.asyncio
async def test_cdp_iam_workload_missing_config_returns_502():
    """FailedPrecondition (workbench 412) → upstream error, not a 401.

    The caller isn't at fault — the deployment is misconfigured. Surfacing
    it as an upstream error tells the operator to check ``CDP_IAM_*`` env
    on the API pod rather than making end users think their token is bad.
    """
    iam_iss = "iamapi.us-west-1.altus.cloudera.com"
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    workbench.set_exchange(status_code=412, body={})
    app = _build_app(_cfg(iam_issuers=frozenset({iam_iss})), upstream, workbench)

    token = _fake_jwt({"iss": iam_iss, "sub": "bob"})
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        resp = await client.post(
            "/mcp",
            headers={"authorization": f"Bearer {token}"},
            json={},
        )
    # UpstreamError → the sidecar surfaces upstream/config failures as 502.
    assert resp.status_code == 502
    assert upstream.requests == []


@pytest.mark.asyncio
async def test_cdp_iam_workload_caches_second_call():
    """Second call within TTL is served from the cache — no re-exchange."""
    iam_iss = "iamapi.us-west-1.altus.cloudera.com"
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    app = _build_app(_cfg(iam_issuers=frozenset({iam_iss})), upstream, workbench)

    token = _fake_jwt({"iss": iam_iss, "sub": "bob"})
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        r1 = await client.post(
            "/mcp", headers={"authorization": f"Bearer {token}"}, json={}
        )
        r2 = await client.post(
            "/mcp", headers={"authorization": f"Bearer {token}"}, json={}
        )

    assert r1.status_code == 200
    assert r2.status_code == 200
    # /exchange hit once, upstream hit twice.
    assert len(workbench.exchange_calls) == 1
    assert len(upstream.requests) == 2


@pytest.mark.asyncio
async def test_client_forged_x_cai_headers_are_stripped():
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    app = _build_app(_cfg(), upstream, workbench)

    key = "a" * 64 + "." + "b" * 64
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        await client.post(
            "/mcp",
            headers={
                "authorization": f"BearerV2 {key}",
                # Attacker attempts to impersonate a different principal by
                # forging the internal header. Sidecar must overwrite it.
                ts.DOWNSTREAM_BEARER_HEADER: "attacker-token",
                ts.PRINCIPAL_HEADER: "root",
            },
            json={},
        )

    fwd = upstream.requests[0]
    assert fwd.headers[ts.DOWNSTREAM_BEARER_HEADER] == key
    assert fwd.headers[ts.PRINCIPAL_HEADER] == "alice"


@pytest.mark.asyncio
async def test_discovery_endpoint_reports_authorization_server():
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    app = _build_app(_cfg(oauth_issuer="https://as.workbench.test/"), upstream, workbench)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        resp = await client.get("/.well-known/oauth-protected-resource")

    assert resp.status_code == 200
    body = resp.json()
    assert body["authorization_servers"] == ["https://as.workbench.test/"]
    assert body["bearer_methods_supported"] == ["header"]


@pytest.mark.asyncio
async def test_discovery_endpoint_path_scoped_variant_is_public():
    """MCP Inspector fetches ``/.well-known/oauth-protected-resource/mcp``
    after a 401 on ``/mcp`` to locate the AS. That path MUST be publicly
    reachable — the sidecar's fallback auth-required route must not
    swallow it. This test locks in the regression fix for the Inspector
    connection failure we saw in the field.
    """
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    app = _build_app(_cfg(oauth_issuer="https://as.workbench.test/"), upstream, workbench)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        resp = await client.get("/.well-known/oauth-protected-resource/mcp")

    assert resp.status_code == 200
    body = resp.json()
    # No Authorization header sent — this endpoint is discovery metadata,
    # not a protected resource.
    assert "www-authenticate" not in {k.lower() for k in resp.headers.keys()}
    assert body["authorization_servers"] == ["https://as.workbench.test/"]
    # Path-scoped variant reflects the suffix in ``resource`` so strict
    # OAuth 2.1 clients can validate resource-URI ↔ metadata alignment.
    assert body["resource"] == "http://sidecar.test/mcp"


@pytest.mark.asyncio
async def test_discovery_endpoint_honors_x_forwarded_proto():
    """Istio terminates TLS at the gateway; inside the pod the request
    arrives over HTTP. Without X-Forwarded-Proto awareness the sidecar
    would advertise ``resource: "http://..."`` on an ``https://`` deploy
    and strict OAuth 2.1 clients would reject the mismatch. Verify both
    the un-scoped and path-scoped shapes reflect the forwarded scheme.
    """
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    app = _build_app(_cfg(oauth_issuer="https://as.workbench.test/"), upstream, workbench)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        resp = await client.get(
            "/.well-known/oauth-protected-resource",
            headers={
                "X-Forwarded-Proto": "https",
                "X-Forwarded-Host": "mcp.example.com",
            },
        )
        resp_scoped = await client.get(
            "/.well-known/oauth-protected-resource/mcp",
            headers={
                "X-Forwarded-Proto": "https",
                "X-Forwarded-Host": "mcp.example.com",
            },
        )

    assert resp.status_code == 200
    assert resp.json()["resource"] == "https://mcp.example.com"
    assert resp_scoped.status_code == 200
    assert resp_scoped.json()["resource"] == "https://mcp.example.com/mcp"


@pytest.mark.asyncio
async def test_www_authenticate_challenge_honors_x_forwarded_proto():
    """The 401 challenge's ``resource_metadata`` URL must be reachable
    from the client — same X-Forwarded-Proto concern as the metadata body
    itself. A client following an ``http://`` metadata URL on an HTTPS
    deployment would either fail the fetch or be downgraded.
    """
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    app = _build_app(_cfg(oauth_issuer="https://as.workbench.test/"), upstream, workbench)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        resp = await client.get(
            "/mcp",
            headers={
                "X-Forwarded-Proto": "https",
                "X-Forwarded-Host": "mcp.example.com",
            },
        )

    assert resp.status_code == 401
    challenge = resp.headers["www-authenticate"]
    assert 'resource_metadata="https://mcp.example.com/' in challenge


@pytest.mark.asyncio
async def test_health_paths_are_not_intercepted_but_forwarded():
    """The sidecar has no health bypass — MCP's /healthz is the health surface.

    Anything not matching the discovery route lands on the fallback and gets
    the same auth treatment. This test locks that in: a GET to /healthz with
    no bearer 401s at the sidecar, so we haven't accidentally opened a hole.
    """
    upstream = _FakeUpstream()
    workbench = _FakeWorkbench()
    app = _build_app(_cfg(), upstream, workbench)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://sidecar.test"
    ) as client:
        resp = await client.get("/healthz")
    assert resp.status_code == 401
