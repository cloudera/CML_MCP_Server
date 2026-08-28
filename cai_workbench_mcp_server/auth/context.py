"""Request-scoped configuration for the HTTP MCP server.

Every ``@mcp.tool()`` in ``http_server.py`` calls ``get_config()`` at entry
and threads the resulting ``{host, api_key, project_id, team}`` dict into
``src.functions.http_helpers.setup_client(host, api_key)``. In stdio mode
that config is process-wide and read from env vars / Docker secrets — one
principal, one process. In HTTP mode the pod fronts many callers, so the
config **must** be scoped to the request that produced it.

We do that with a single :class:`contextvars.ContextVar` set by the
Starlette auth middleware once per request. FastMCP tool bodies run inside
the request's asyncio task, so ``ContextVar.get()`` returns the value the
middleware installed — and never leaks across concurrent requests.

Design notes:

- The middleware receives ``X-CAI-Downstream-Bearer`` from the translation
  sidecar (already validated and, if needed, exchanged for an APIv2-audience
  token). That header value is the ``api_key`` in the config dict; the tool
  layer treats it as an opaque bearer, exactly as it treats an API key
  supplied via env in stdio mode.
- ``project_id`` and ``team`` are ``None`` here. Tools that need a
  project_id read it from their ``params`` (with a per-call fallback path),
  which was already the shape used in stdio mode too — nothing changes.
- We deliberately raise :class:`NoRequestConfigError` when the ContextVar
  is unset. Falling back to module-level env vars is exactly the
  single-tenant bug we're fixing: it would silently run the tool as whoever
  owns the mounted secrets instead of failing loudly.
"""

from __future__ import annotations

import contextvars
from typing import Any, Dict, Optional


class NoRequestConfigError(RuntimeError):
    """Raised when :func:`get_request_config` is called outside a request.

    In HTTP mode this indicates a bug: a tool ran without the auth
    middleware having populated the ContextVar. In stdio mode it indicates
    the wrong ``get_config()`` was called (stdio uses its own env-based
    implementation and does not consult this ContextVar).
    """


# The ContextVar itself. ``default=None`` means "unset"; the middleware sets
# a real dict on every valid request. We never set a real default here
# because a stale default would be worse than raising.
request_config: contextvars.ContextVar[Optional[Dict[str, Any]]] = (
    contextvars.ContextVar("cai_workbench_mcp_request_config", default=None)
)


def set_request_config(config: Dict[str, Any]) -> contextvars.Token:
    """Install ``config`` for the duration of the current request.

    Returns the ``Token`` from ``ContextVar.set`` so the caller can restore
    the previous value in a ``finally`` block. Middleware typically doesn't
    need to reset explicitly — the task-local context goes out of scope
    when the request finishes — but resetting is cheap and makes tests
    easier to reason about.
    """
    return request_config.set(config)


def get_request_config() -> Dict[str, Any]:
    """Return the current request's config dict.

    Raises :class:`NoRequestConfigError` if the middleware hasn't set one,
    which is treated as a programming error, not a client-facing failure.
    """
    value = request_config.get()
    if value is None:
        raise NoRequestConfigError(
            "request_config is unset — the HTTP auth middleware did not run "
            "for this request. On the pod, this means the translation "
            "sidecar's X-CAI-Downstream-Bearer header was missing and the "
            "middleware should have already returned 401 before reaching a "
            "tool body."
        )
    return value
