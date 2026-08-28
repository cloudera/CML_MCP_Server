"""Per-request auth plumbing for the HTTP MCP server.

This package exists only for the HTTP entry point. The stdio server keeps its
env-var / secret-file configuration path and does not import from here.

The public surface is intentionally small:

- :data:`request_config` — the ``ContextVar`` that carries the current
  request's ``{host, api_key, project_id, team}`` dict for the duration of
  a single MCP tool invocation.
- :func:`get_request_config` — read the ContextVar and raise if it is unset.
  Used by ``http_server.get_config()`` so every tool automatically picks up
  the caller's identity.
- :func:`set_request_config` — write the ContextVar and return the reset
  token. Called by the Starlette auth middleware once per request.
"""

from .context import (
    NoRequestConfigError,
    get_request_config,
    request_config,
    set_request_config,
)
from .middleware import (
    DOWNSTREAM_BEARER_HEADER,
    DownstreamBearerMiddleware,
    PRINCIPAL_HEADER,
    resolve_workbench_host,
)

__all__ = [
    "DOWNSTREAM_BEARER_HEADER",
    "DownstreamBearerMiddleware",
    "NoRequestConfigError",
    "PRINCIPAL_HEADER",
    "get_request_config",
    "request_config",
    "resolve_workbench_host",
    "set_request_config",
]
