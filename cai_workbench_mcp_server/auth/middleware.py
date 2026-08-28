"""Starlette middleware that turns a sidecar-authenticated request into a
populated :data:`request_config` ContextVar for the tool layer to consume.

This module is the entire auth boundary of the MCP server process. The
translation sidecar has already:

- classified the client's ``Authorization: Bearer <token>`` as either an
  APIv2 API key / web JWT (verified via ``/api/v2/auth/validate_key``) or a
  MCP OAuth access token (verified against the workbench AS JWKS and
  exchanged via ``/api/v2/auth/exchange`` for an APIv2-audience token);
- stripped the inbound ``Authorization`` header entirely;
- injected two new headers into the loopback request:

  - ``X-CAI-Downstream-Bearer`` — the APIv2-audience bearer we should hand
    to ``cmlapi``. This is the authoritative signal.
  - ``X-CAI-Principal`` — the workbench username, for logs only. **Never**
    consulted for authorization.

The middleware refuses any request that omits ``X-CAI-Downstream-Bearer``
with 401 and a stern log line. The MCP server binds to loopback in the pod,
so the only way to reach this port with no sidecar header is via
``kubectl exec`` — which we treat as an intrusion attempt rather than a
misconfiguration.

The middleware is deliberately dumb: no token parsing, no JWKS, no cache.
All of that is the sidecar's job. Keeping this thin means the surface area
inside the FastMCP process (which loads ~100 tool implementations and a
large dependency graph) stays minimal.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from .context import request_config

logger = logging.getLogger(__name__)

# Header names are lowercased when Starlette exposes them via ``request.headers``,
# so we normalise on lookup rather than trusting the caller's casing.
DOWNSTREAM_BEARER_HEADER = "x-cai-downstream-bearer"
PRINCIPAL_HEADER = "x-cai-principal"

# Paths that must remain open even without a bearer. These are health probes
# hit by kubelet on the loopback interface — the sidecar is not involved.
# We keep this list tight; every non-listed path is auth-gated.
_UNAUTHED_PATHS = frozenset({"/healthz", "/readyz"})


class DownstreamBearerMiddleware(BaseHTTPMiddleware):
    """Enforce the sidecar contract and populate :data:`request_config`.

    Parameters
    ----------
    app:
        The wrapped ASGI application (FastMCP's Streamable HTTP app).
    workbench_host:
        The workbench base URL. This is process-wide, injected by the Helm
        chart via ``CAI_WORKBENCH_HOST``, and identical for every request
        the pod serves. It lives on the config dict so ``setup_client`` can
        find it without a second env lookup.
    """

    def __init__(self, app: ASGIApp, workbench_host: str) -> None:
        super().__init__(app)
        self._workbench_host = workbench_host

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        # Health checks bypass auth. Everything else needs the sidecar header.
        if request.url.path in _UNAUTHED_PATHS:
            return await call_next(request)

        bearer = request.headers.get(DOWNSTREAM_BEARER_HEADER)
        if not bearer:
            # Log once with enough context to spot a rogue caller, but never
            # log the request body or any header value that might carry a
            # secret (e.g. someone hitting the loopback port with a raw
            # Authorization: Bearer they hoped would work).
            logger.warning(
                "refusing MCP request without %s (path=%s, remote=%s)",
                DOWNSTREAM_BEARER_HEADER,
                request.url.path,
                request.client.host if request.client else "unknown",
            )
            return JSONResponse(
                {
                    "error": "missing_sidecar_bearer",
                    "detail": (
                        "This MCP endpoint is only reachable via the "
                        "translation sidecar. Direct access is refused."
                    ),
                },
                status_code=401,
            )

        principal: Optional[str] = request.headers.get(PRINCIPAL_HEADER)

        # Build the same-shaped dict get_config() historically returned.
        # project_id / team stay None: tools that need a project accept it
        # per-call in ``params``, which was already the fallback behaviour
        # in stdio mode.
        config: Dict[str, Any] = {
            "host": self._workbench_host,
            "api_key": bearer,
            "project_id": None,
            "team": None,
            "principal": principal,
        }

        token = request_config.set(config)
        try:
            response: Response = await call_next(request)
        finally:
            # Reset explicitly. The task-local context would drop the value
            # on its own, but resetting keeps tests deterministic and makes
            # accidental reuse (e.g. a background task started from within
            # the handler) fail loudly instead of silently inheriting the
            # previous caller's bearer.
            request_config.reset(token)
        return response


def resolve_workbench_host() -> str:
    """Return the workbench base URL, or raise if it isn't configured.

    In the pod, the Helm chart injects ``CAI_WORKBENCH_HOST`` pointing at
    the in-cluster APIv2 service. Locally, developers can set the same env
    var by hand. We fail fast at startup rather than at first tool call —
    a missing host is a deploy-time bug, not a per-request one.
    """
    host = os.environ.get("CAI_WORKBENCH_HOST", "").strip()
    if not host:
        raise RuntimeError(
            "CAI_WORKBENCH_HOST is not set. The HTTP MCP server needs the "
            "workbench base URL to construct cmlapi clients; the Helm chart "
            "injects this env var at deploy time."
        )
    return host
