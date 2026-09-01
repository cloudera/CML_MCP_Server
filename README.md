# Cloudera AI Workbench MCP Server

A Model Context Protocol (MCP) server for Cloudera AI workbench built with FastMCP, enabling LLMs to interact with Cloudera AI Workbench APIs.

## Features

### Cloudera AI Integration
- **File Management**: Upload files and folders with directory structure preservation
- **Job Management**: Create, run, monitor, and delete jobs
- **Model Lifecycle**: Build, deploy, and manage ML models
- **Experiment Tracking**: Log metrics, parameters, and manage experiment runs
- **Project Operations**: Project discovery, file listing, and metadata management
- **Application Management**: Create, update, and manage applications

### Transport Modes
1. **STDIO** (Recommended): Secure subprocess communication for local/Claude Desktop use
2. **HTTP**: Simple HTTP API for development/testing (no authentication)

## Prerequisites

- Python 3.10+
- A Cloudera AI instance and API key
- `uv` / `uvx` ([install uv](https://docs.astral.sh/uv/getting-started/installation/))

See [SETUP.md](./SETUP.md) for full installation options (Agent Studio, Cursor, local venv, Docker).

## Architecture

All API tools use the official **`cmlapi` Python SDK** (`CMLServiceApi`) rather than raw HTTP requests. A shared `setup_client()` in `http_helpers.py` creates a configured client; each tool function is a thin wrapper around the corresponding SDK method. This eliminates URL construction bugs, provides typed request/response objects, and ensures correct endpoint paths (e.g. `:restart` vs `/restart`).

## Quick Start

Use **`uvx`** with **`--with`** to install `cmlapi` from your Cloudera AI instance at runtime. This works in [Agent Studio](https://docs.cloudera.com/machine-learning/cloud/use-ai-studios/topics/ml-agent-studio-overview.html), Cursor, and other MCP clients — no Docker required.

Replace `ml-xxxx.cloudera.site`, `your-api-key`, and `your-project-id` with your values:

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
        "CAI_WORKBENCH_PROJECT_ID": "your-project-id"
      }
    }
  }
}
```

The `--with` argument is **required** — without it, API tools fail with `No module named 'cmlapi'`.

For local venv, Docker, branch pinning, Cursor config, and troubleshooting, see **[SETUP.md](./SETUP.md)**.

## Usage

STDIO mode (via `uvx` above) is recommended for Agent Studio, Cursor, and Claude Desktop. For local venv, Docker, and running from a checkout, see **[SETUP.md](./SETUP.md)**.

### HTTP Mode (Development Only)

⚠️ **Warning**: HTTP mode runs without authentication - use only for local development!

```bash
# Start HTTP server on port 8000
uv run -m cai_workbench_mcp_server.http_server

# Or use the shortcut
uvx --from . cai-workbench-mcp-http
```

#### Available Endpoints

1. **MCP Protocol Endpoint**: `/mcp-api` (simplified MCP protocol)
   ```bash
   # List tools
   curl -X POST http://localhost:8000/mcp-api \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "id": "1", "method": "tools/list", "params": {}}'
   
   # Call a tool
   curl -X POST http://localhost:8000/mcp-api \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0", 
       "id": "2", 
       "method": "tools/call",
       "params": {
         "name": "list_projects_tool",
         "arguments": {}
       }
     }'
   ```

2. **Debug Endpoints** (bypass MCP protocol):
   ```bash
   # Test server status
   curl http://localhost:8000/test
   
   # List all tools
   curl http://localhost:8000/debug/tools
   
   # Call any tool directly
   curl -X POST http://localhost:8000/debug/call \
     -H "Content-Type: application/json" \
     -d '{"tool": "list_projects_tool", "params": {}}'
   ```

#### Client Connection Examples

Using MCP clients:
```bash
# FastMCP client
cloudera-mcp chat http-stateless http://localhost:8000/mcp-api

# Python client
from fastmcp import Client
client = Client("http://localhost:8000/mcp-api")
```

## Available Tools (164 total)

The server exposes **164** tools. The authoritative list is whatever the running server returns from MCP `tools/list` or `GET /debug/tools`. Below is a grouped overview.

### Project management
- `list_projects_tool`, `get_project_id_tool`, `get_project_tool`, `create_project_tool`, `update_project_tool`, `delete_project_tool`
- `create_amp_tool`, `batch_list_projects_tool`, `list_project_names_tool`
- `list_project_collaborators_tool`, `add_project_collaborator_tool`, `delete_project_collaborator_tool`
- `list_all_run_as_machine_user_collaborators_tool`

### File operations
- `upload_file_tool`, `upload_folder_tool`, `list_project_files_tool`, `delete_project_file_tool`, `update_project_file_metadata_tool`, `download_project_file_tool`

### Jobs
- `create_job_tool`, `list_jobs_tool`, `get_job_tool`, `update_job_tool`, `delete_job_tool`, `delete_all_jobs_tool`
- `create_job_run_tool`, `list_job_runs_tool`, `get_job_run_tool`, `stop_job_run_tool`
- `list_job_dependencies_tool`
- Workspace-wide: `list_all_jobs_tool`

### Models (deployments & builds)
- `list_models_tool`, `get_model_tool`, `create_model_tool`, `update_model_tool`, `delete_model_tool`
- `create_model_build_tool`, `list_model_builds_tool`, `get_model_build_tool`, `delete_model_build_tool`
- `create_model_deployment_tool`, `list_model_deployments_tool`, `get_model_deployment_tool`, `stop_model_deployment_tool`, `restart_model_deployment_tool`
- Workspace-wide: `list_all_models_tool`

### Model registry (MLflow-linked)
- `list_registered_models_tool`, `create_registered_model_tool`, `get_registered_model_tool`, `update_registered_model_tool`, `delete_registered_model_tool`
- `get_registered_model_version_tool`, `update_registered_model_version_tool`, `delete_registered_model_version_tool`

### Experiments
- Per-project: `create_experiment_tool`, `list_experiments_tool`, `get_experiment_tool`, `update_experiment_tool`, `delete_experiment_tool`
- Runs: `create_experiment_run_tool`, `get_experiment_run_tool`, `update_experiment_run_tool`, `delete_experiment_run_tool`, `delete_experiment_run_batch_tool`, `log_experiment_run_batch_tool`
- Workspace-wide: `list_all_experiments_tool`, `list_experiment_runs_tool`, `get_experiment_run_metrics_tool`

### Applications
- `create_application_tool`, `list_applications_tool`, `get_application_tool`, `update_application_tool`, `restart_application_tool`, `stop_application_tool`, `delete_application_tool`
- `get_application_dashboard_tool`

### Runtimes, repos, Docker, API keys
- `get_runtimes_tool`, `list_runtimes_tool`, `list_runtime_addons_tool`, `register_custom_runtime_tool`, `validate_custom_runtime_tool`, `update_runtime_status_tool`, `update_runtime_addon_status_tool`
- `list_runtime_repos_tool`, `create_runtime_repo_tool`, `update_runtime_repo_tool`, `delete_runtime_repo_tool`
- `list_docker_credentials_tool`, `create_docker_credential_tool`, `update_docker_credential_tool`, `delete_docker_credential_tool`, `set_docker_credential_tool`
- `list_v2_keys_tool`, `create_v2_key_tool`, `delete_v2_key_tool`, `delete_v2_keys_tool`, `validate_api_key_tool`, `validate_api_key_v2_tool`, `rotate_v1_key_tool`

### Teams & synced teams
- `list_teams_tool`, `create_team_tool`, `delete_team_tool`
- `create_synced_team_tool`, `list_synced_team_groups_tool`, `add_group_to_synced_team_tool`, `remove_group_from_synced_team_tool`, `update_group_permission_for_synced_team_tool`
- `list_synced_team_members_tool`, `update_member_permission_for_synced_team_tool`

### Users
- `get_short_user_by_id_tool`

### Quotas & resource management
- `list_cpu_profiles_tool`, `create_cpu_profile_tool`, `update_cpu_profile_tool`, `delete_cpu_profile_tool`
- `list_users_quota_tool`, `list_groups_quota_tool`, `list_teams_accelerator_quota_tool`, `list_users_accelerator_quota_tool`
- `get_default_quota_tool`, `get_default_quotas_tool`, `set_default_quota_tool`, `set_team_default_quota_tool`
- `list_all_resource_groups_tool`, `update_resource_group_tool`
- `list_all_accelerator_node_labels_tool`
- `create_accelerator_node_label_gpu_profile_tool`, `update_accelerator_node_label_gpu_profile_tool`, `delete_accelerator_node_label_gpu_profile_tool`
- `update_accelerator_labels_admin_config_tool`, `update_accelerator_labels_default_quota_tool`
- `list_accelerator_based_user_quota_tool`, `update_accelerator_based_user_quota_tool`
- `list_accelerator_based_team_quota_tool`, `update_accelerator_based_team_quota_tool`

### Copilot models
- `list_copilot_models_tool`, `get_copilot_model_tool`, `create_copilot_model_tool`, `update_copilot_model_tool`, `delete_copilot_model_tool`
- `list_copilot_embedding_models_tool`, `get_copilot_embedding_model_tool`, `create_copilot_embedding_model_tool`, `update_copilot_embedding_model_tool`, `delete_copilot_embedding_model_tool`
- `send_copilot_event_tool`

### Spark & platform configuration
- `set_workspace_spark_default_tool`, `read_workspace_spark_default_tool`, `read_cml_spark_default_tool`, `read_base_cluster_spark_default_tool`
- `disable_engines_tool`, `set_workbench_tls_secret_tool`, `dashboards_archive_tool`

### Sync status
- `latest_sync_status_tool`, `users_sync_status_tool`, `teams_sync_status_tool`

### Workload, usage & monitoring
- `list_usage_tool`, `get_time_series_tool`
- `list_ml_serving_apps_tool`, `list_workload_executions_tool`, `list_workload_status_tool`, `list_workload_types_tool`
- `list_news_feeds_tool`

### Diagnostics & health
- `health_check_tool`, `generate_diag_bundle_tool`, `get_diag_bundle_status_tool`, `download_diag_bundle_tool`


## Examples

### Upload and Run a Job

```python
# 1. Upload your script
upload_file_tool(
    file_path="train.py",
    target_dir="scripts/"
)

# 2. Create a job
create_job_tool(
    name="Model Training",
    script="scripts/train.py",
    cpu=2,
    memory=4,
    runtime_identifier="python3.9-standard"
)

# 3. Run the job
create_job_run_tool(
    project_id="your-project-id",
    job_id="created-job-id"
)
```

### Deploy a Model

```python
# 1. Create model build
create_model_build_tool(
    project_id="your-project-id",
    model_id="your-model-id",
    file_path="model.py",
    function_name="predict"
)

# 2. Deploy the model
create_model_deployment_tool(
    project_id="your-project-id",
    model_id="your-model-id", 
    build_id="created-build-id",
    name="Production Deployment"
)
```

## Troubleshooting

See **[SETUP.md — Common issues](./SETUP.md#common-issues)** for `cmlapi`, SSL, Docker, and authentication problems.

## Security Notes

- **STDIO Mode**: Secure - credentials in environment variables
- **HTTP Mode**: No authentication - development only!
- **Production**: Always use STDIO mode or deploy with proper security

## Related Resources

- [Cloudera AI Workbench](https://docs.cloudera.com/machine-learning/1.5.5/workspaces-privatecloud/topics/ml-pvc-provision-ml-workspace.html) - Cloudera AI documentation
- [FastMCP](https://gofastmcp.com/) - The MCP framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification

---

## Legal Notice

**IMPORTANT: Please read the following before proceeding.**

Cloudera, Inc. ("Cloudera") makes available to you this optional software, which may include accelerators for machine learning projects ("AMPs"), Hugging Face Spaces, or AI models, constitutes reference machine learning projects ("Reference Projects"). By configuring and launching this Reference Project, you acknowledge and assume the risk that using Reference Projects may (i) cause third party software, such as third-party large language models, to be downloaded directly into your environment and/or (ii) enable third-party services, such as third-party AI services, and transmission of data and metadata to such third-party services providers. Any such third-party software is not validated or maintained by Cloudera. Any support provided for Reference Projects is at Cloudera's sole discretion. You agree to comply with any applicable license terms or terms of use, including any third-party license terms, for Reference Projects.

If you do not wish to download and install the third party software packages, do not configure, launch or otherwise use this Reference Project. By configuring, launching or otherwise using the Reference Project, you acknowledge the foregoing statement and agree that Cloudera is not responsible or liable in any way for any third party software packages.

*Copyright (c) 2025 - Cloudera, Inc. All rights reserved.*

