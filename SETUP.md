# Setup Guide

Complete installation and configuration for the Cloudera AI Workbench MCP Server.

## Choose your setup path

| Use case | Approach | `cmlapi` install |
|----------|----------|------------------|
| **Agent Studio / CAI Workbench** | `uvx --with` (recommended) | Runtime via `--with` URL |
| **Cursor / local IDE** | `uvx --with` or local venv | Runtime via `--with` or `uv pip install` |
| **Claude Desktop (local)** | Docker or `uvx --with` | Build time or runtime |

Agent Studio and in-cluster workbench environments typically **do not** have Docker Desktop. Use **`uvx --with`**, not `docker run`.

---

## Installing cmlapi

The `cmlapi` Python SDK is served by **your** Cloudera AI instance at:

```text
https://<your-ml-host>/api/v2/python.tar.gz
```

It is intentionally **not** listed in `pyproject.toml` because the URL is different for every deployment. Do **not** run `pip install cmlapi` — that package does not exist on PyPI.

| Setup | How `cmlapi` is installed |
|-------|---------------------------|
| **Agent Studio / Cursor (`uvx`)** | `--with https://<host>/api/v2/python.tar.gz` in MCP args |
| **Local venv** | `uv pip install https://<host>/api/v2/python.tar.gz` after `uv sync` |
| **Docker** | Automatically at **image build** time via `CAI_WORKBENCH_HOST` |

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CAI_WORKBENCH_HOST` | Yes | Full URL to your CAI workbench instance (e.g. `https://ml-xxxx.cloudera.site`) |
| `CAI_WORKBENCH_API_KEY` | Yes | Your CAI API key |
| `CAI_WORKBENCH_PROJECT_ID` | No | Default project ID for tools that need one |
| `CAI_WORKBENCH_TEAM` | No | Default team **username** for `create_project_tool` (see [Team username](#team-username-for-project-creation) below) |

### Team username for project creation

There is **no fixed team name** across deployments. Each workbench has its own teams.

The API field is `CreateProjectRequest.team_name`, and it must be the team **username** (from `CreateTeamRequest.username`), **not** the display name. For example, a team may show as "Team 1" in the UI but its username might be `Team1` — on another deployment it could be `ml-platform`, `data-science`, etc.

How to find yours:

1. Call **`list_teams_tool`** — works when your API key can read team/group quota APIs.
2. Ask a workspace admin for the team username.
3. Inspect an existing team-owned project in the UI or via `list_projects_tool` (owner username).

Set `CAI_WORKBENCH_TEAM` only when you always create projects under the same team (common on team-only workspaces). Otherwise pass `team_name` per call to `create_project_tool`.

---

## Option A: Agent Studio / Cursor (`uvx`) — recommended

Replace `ml-xxxx.cloudera.site`, `your-api-key`, `your-project-id`, and (if needed) `your-team-username` with your values:

```json
{
  "mcpServers": {
    "cloudera-ai": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/cloudera/CAI_Workbench_MCP_Server.git",
        "--with",
        "https://ml-xxxx.cloudera.site/api/v2/python.tar.gz",
        "cai-workbench-mcp-stdio"
      ],
      "env": {
        "CAI_WORKBENCH_HOST": "https://ml-xxxx.cloudera.site",
        "CAI_WORKBENCH_API_KEY": "your-api-key",
        "CAI_WORKBENCH_PROJECT_ID": "your-project-id",
        "CAI_WORKBENCH_TEAM": "your-team-username"
      }
    }
  }
}
```

The `--with` line is **required**. Without it, tools fail with `No module named 'cmlapi'`.

Restart your MCP client (Agent Studio, Cursor, etc.) and verify with MCP `tools/list`.

### Cursor: local checkout (active development)

When developing from a clone and running from your working tree:

```bash
git clone https://github.com/cloudera/CAI_Workbench_MCP_Server.git
cd CAI_Workbench_MCP_Server
uv sync
uv pip install https://ml-xxxx.cloudera.site/api/v2/python.tar.gz
```

```json
{
  "mcpServers": {
    "cai-workbench-local": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/ABSOLUTE/PATH/TO/CAI_Workbench_MCP_Server",
        "-m",
        "cai_workbench_mcp_server.stdio_server"
      ],
      "env": {
        "CAI_WORKBENCH_HOST": "https://ml-xxxx.cloudera.site",
        "CAI_WORKBENCH_API_KEY": "your-api-key",
        "CAI_WORKBENCH_PROJECT_ID": "your-project-id",
        "CAI_WORKBENCH_TEAM": "your-team-username"
      }
    }
  }
}
```

Restart the MCP server after pulling or changing code.

### Pin a branch, tag, or commit (optional)

Append `@ref` to the Git URL (PEP 440 VCS URL syntax):

| Target | Example suffix on the repo URL |
|--------|----------------------------------|
| Branch | `...git@dev` |
| Tag | `...git@v2.1.0` |
| Commit SHA | `...git@a1b2c3d4` |

Example with a release tag:

```json
{
  "mcpServers": {
    "cloudera-ai": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/cloudera/CAI_Workbench_MCP_Server.git@v2.1.0",
        "--with",
        "https://ml-xxxx.cloudera.site/api/v2/python.tar.gz",
        "cai-workbench-mcp-stdio"
      ],
      "env": {
        "CAI_WORKBENCH_HOST": "https://ml-xxxx.cloudera.site",
        "CAI_WORKBENCH_API_KEY": "your-api-key",
        "CAI_WORKBENCH_PROJECT_ID": "your-project-id",
        "CAI_WORKBENCH_TEAM": "your-team-username"
      }
    }
  }
}
```

**`uvx` caches aggressively.** When testing unreleased changes, force a fresh pull:

```bash
uvx --no-cache \
  --from "git+https://github.com/cloudera/CAI_Workbench_MCP_Server.git@v2.1.0" \
  --with "https://ml-xxxx.cloudera.site/api/v2/python.tar.gz" \
  cai-workbench-mcp-stdio
```

Or clear the cache:

```bash
uv cache clean
```

---

## Option B: Local venv development

### Step 1: Clone and sync

```bash
git clone https://github.com/cloudera/CAI_Workbench_MCP_Server.git
cd CAI_Workbench_MCP_Server
uv sync
```

### Step 2: Install cmlapi from your instance

```bash
uv pip install https://ml-xxxx.cloudera.site/api/v2/python.tar.gz
```

### Step 3: Configure and run

```bash
export CAI_WORKBENCH_HOST=https://ml-xxxx.cloudera.site
export CAI_WORKBENCH_API_KEY=your-api-key
export CAI_WORKBENCH_PROJECT_ID=your-project-id   # optional
export CAI_WORKBENCH_TEAM=your-team-username   # optional; team username on your workbench
uv run -m cai_workbench_mcp_server.stdio_server
```

Or run via `uvx` from the repo root (installs `cmlapi` via `--with`):

```bash
export CAI_WORKBENCH_HOST=https://ml-xxxx.cloudera.site
export CAI_WORKBENCH_API_KEY=your-api-key
uvx --from . --with https://ml-xxxx.cloudera.site/api/v2/python.tar.gz cai-workbench-mcp-stdio
```

---

## Option C: Docker (local Claude Desktop)

Use this when you have Docker Desktop or a Docker engine on your **local machine**. The image installs `cmlapi` at **build** time.

### Step 1: Clone and set host

```bash
git clone https://github.com/cloudera/CAI_Workbench_MCP_Server.git
cd CAI_Workbench_MCP_Server
export CAI_WORKBENCH_HOST=https://ml-xxxx.cloudera.site
```

The build machine must be able to reach this URL to download `cmlapi`.

### Step 2: Build and test

```bash
make build
make test
make run
```

### Step 3: Claude Desktop configuration

**Simple (environment variables):**

```json
{
  "mcpServers": {
    "cai_workbench_mcp": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "CAI_WORKBENCH_HOST=https://ml-xxxx.cloudera.site",
        "-e", "CAI_WORKBENCH_API_KEY=your-api-key",
        "cai-workbench-mcp-server"
      ]
    }
  }
}
```

**Secure (Docker secrets — recommended for production-like use):**

```json
{
  "mcpServers": {
    "cai_workbench_mcp": {
      "command": "docker-compose",
      "args": [
        "-f",
        "/absolute/path/to/cai_workbench_mcp_server/docker-compose.secrets.yml",
        "run", "--rm", "cai-workbench-mcp-server"
      ]
    }
  }
}
```

See [DOCKER.md](./DOCKER.md) for Docker secrets and advanced options.

---

## Common issues

**"Missing required configuration"**
- Set `CAI_WORKBENCH_HOST` and `CAI_WORKBENCH_API_KEY` in the MCP `env` block

**"No module named 'cmlapi'" (uvx / Agent Studio)**
- Missing `--with "https://<host>/api/v2/python.tar.gz"` in MCP args
- Check that your workbench host is reachable from the agent runtime

**"No module named 'cmlapi'" (local venv)**
- Run: `uv pip install https://<host>/api/v2/python.tar.gz`

**Build fails with "No module named 'cmlapi'" (Docker)**
- Set `CAI_WORKBENCH_HOST` before `make build`
- Ensure the build machine can reach your CAI instance

**Claude Desktop shows JSON parse errors**
- Use STDIO mode, not HTTP mode
- Rebuild the Docker image if using Option C

**SSL / certificate verification errors (PvC, Agent Studio)**
- Use a release that includes the system CA bundle fix in `http_helpers.py` (e.g. `v2.1.0` or later)
- Pin the Git URL to that tag if needed: `...git@v2.1.0`

**"Object of type datetime is not JSON serializable"**
- Upgrade to the latest release — `serialize_result()` handles this

**HTTP connection issues (dev mode)**
- Start the server: `uv run -m cai_workbench_mcp_server.http_server`
- Default port is 8000; test with `curl http://localhost:8000/test`

**Tool not found**
- Check tool name spelling (use MCP `tools/list`)

**API authentication errors**
- Verify `CAI_WORKBENCH_API_KEY` is valid
- Ensure `CAI_WORKBENCH_HOST` includes the `https://` prefix
