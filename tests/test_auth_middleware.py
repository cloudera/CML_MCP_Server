"""Unit tests for the MCP-side downstream bearer middleware.

The middleware is deliberately dumb: it enforces that every request
carries the sidecar-injected ``X-CAI-Downstream-Bearer`` header and
converts it into a populated ``request_config`` ContextVar for the tool
layer. These tests lock in that contract, including the tricky bit —
that two concurrent requests never see each other's config value.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List

import httpx
import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from cai_workbench_mcp_server.auth import (
    DOWNSTREAM_BEARER_HEADER,
    DownstreamBearerMiddleware,
    NoRequestConfigError,
    PRINCIPAL_HEADER,
    get_request_config,
    request_config,
)


def _make_app(recorder: List[Dict[str, Any]]) -> Starlette:
    """Build a tiny app that echoes the current request_config back."""

    async def echo(request):  # noqa: ANN001 — Starlette handler signature
        cfg = get_request_config()
        recorder.append(dict(cfg))
        return JSONResponse(cfg)

    async def health(request):  # noqa: ANN001
        return JSONResponse({"status": "ok"})

    app = Starlette(
        routes=[
            Route("/echo", echo, methods=["GET", "POST"]),
            Route("/healthz", health, methods=["GET"]),
        ],
    )
    app.add_middleware(DownstreamBearerMiddleware, workbench_host="http://wb.test")
    return app


@pytest.mark.asyncio
async def test_missing_downstream_header_returns_401():
    app = _make_app([])
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://mcp.test"
    ) as client:
        resp = await client.post("/echo")
    assert resp.status_code == 401
    assert resp.json()["error"] == "missing_sidecar_bearer"


@pytest.mark.asyncio
async def test_health_paths_bypass_auth():
    app = _make_app([])
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://mcp.test"
    ) as client:
        resp = await client.get("/healthz")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_valid_header_populates_context():
    recorder: List[Dict[str, Any]] = []
    app = _make_app(recorder)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://mcp.test"
    ) as client:
        resp = await client.post(
            "/echo",
            headers={
                DOWNSTREAM_BEARER_HEADER: "token-abc",
                PRINCIPAL_HEADER: "alice",
            },
        )
    assert resp.status_code == 200
    assert recorder == [
        {
            "host": "http://wb.test",
            "api_key": "token-abc",
            "project_id": None,
            "team": None,
            "principal": "alice",
        }
    ]


@pytest.mark.asyncio
async def test_context_reset_between_requests():
    """After the middleware returns, ``request_config`` must be unset."""
    recorder: List[Dict[str, Any]] = []
    app = _make_app(recorder)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://mcp.test"
    ) as client:
        await client.post(
            "/echo",
            headers={DOWNSTREAM_BEARER_HEADER: "token-abc"},
        )

    # Outside any request, the ContextVar is unset and get_request_config
    # raises. This is the guard against tools accidentally running as the
    # last caller when triggered from a background task.
    with pytest.raises(NoRequestConfigError):
        get_request_config()


@pytest.mark.asyncio
async def test_concurrent_requests_do_not_leak_config():
    """Two overlapping requests must see distinct ``request_config`` values.

    We serve each request from an in-app coroutine that records what
    ``get_request_config()`` returns *after* an asyncio hop, forcing a
    task switch mid-handler. If the ContextVar were process-global (bug),
    both handlers would see whichever request set its config last.
    """
    seen: Dict[str, Dict[str, Any]] = {}
    gate = asyncio.Event()

    async def echo(request):  # noqa: ANN001
        tag = request.headers.get("x-tag", "?")
        # Yield until both requests are inside the handler at once. If the
        # ContextVar isn't per-task, the second request's set() would
        # overwrite the first and both handlers would record the same value.
        gate.set()
        await asyncio.sleep(0.01)
        seen[tag] = dict(get_request_config())
        return JSONResponse({"tag": tag})

    app = Starlette(routes=[Route("/echo", echo, methods=["GET", "POST"])])
    app.add_middleware(DownstreamBearerMiddleware, workbench_host="http://wb.test")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://mcp.test"
    ) as client:

        async def call(tag: str, token: str) -> None:
            await client.post(
                "/echo",
                headers={
                    "x-tag": tag,
                    DOWNSTREAM_BEARER_HEADER: token,
                    PRINCIPAL_HEADER: tag,
                },
            )

        await asyncio.gather(
            call("alice", "token-alice"),
            call("bob", "token-bob"),
        )

    assert seen["alice"]["api_key"] == "token-alice"
    assert seen["alice"]["principal"] == "alice"
    assert seen["bob"]["api_key"] == "token-bob"
    assert seen["bob"]["principal"] == "bob"


@pytest.mark.asyncio
async def test_principal_header_optional():
    """Missing X-CAI-Principal should not fail — it's informational only."""
    recorder: List[Dict[str, Any]] = []
    app = _make_app(recorder)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://mcp.test"
    ) as client:
        resp = await client.post(
            "/echo",
            headers={DOWNSTREAM_BEARER_HEADER: "token-only"},
        )
    assert resp.status_code == 200
    assert recorder[0]["principal"] is None
    assert recorder[0]["api_key"] == "token-only"
