#!/usr/bin/env python3
"""
Cloudera AI Workbench MCP HTTP Server - Simplified HTTP-only implementation
"""

import os
import json
from typing import Dict, Any
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all the implementation functions
from .src.functions.upload_folder import upload_folder
from .src.functions.upload_file import upload_file
from .src.functions.create_job import create_job
from .src.functions.list_jobs import list_jobs
from .src.functions.delete_job import delete_job
from .src.functions.delete_all_jobs import delete_all_jobs
from .src.functions.get_project_id import get_project_id
from .src.functions.create_job_run import create_job_run
from .src.functions.create_experiment import create_experiment
from .src.functions.create_experiment_run import create_experiment_run
from .src.functions.create_model_build import create_model_build
from .src.functions.create_model_deployment import create_model_deployment
from .src.functions.create_application import create_application
from .src.functions.list_registered_models import list_registered_models
from .src.functions.create_registered_model import create_registered_model
from .src.functions.update_registered_model import update_registered_model
from .src.functions.get_registered_model import get_registered_model
from .src.functions.delete_registered_model import delete_registered_model
from .src.functions.update_registered_model_version import update_registered_model_version
from .src.functions.get_registered_model_version import get_registered_model_version
from .src.functions.delete_registered_model_version import delete_registered_model_version
from .src.functions.create_project import create_project
from .src.functions.get_project import get_project
from .src.functions.delete_project import delete_project
from .src.functions.list_project_names import list_project_names
from .src.functions.list_project_collaborators import list_project_collaborators
from .src.functions.delete_project_collaborator import delete_project_collaborator
from .src.functions.add_project_collaborator import add_project_collaborator
from .src.functions.list_all_experiments import list_all_experiments
from .src.functions.list_experiment_runs import list_experiment_runs
from .src.functions.get_experiment_run_metrics import get_experiment_run_metrics
from .src.functions.list_all_jobs import list_all_jobs
from .src.functions.list_all_models import list_all_models
from .src.functions.create_model import create_model
from .src.functions.update_model import update_model
from .src.functions.delete_model_build import delete_model_build
from .src.functions.restart_model_deployment import restart_model_deployment
from .src.functions.download_project_file import download_project_file
from .src.functions.delete_application import delete_application
from .src.functions.delete_experiment import delete_experiment
from .src.functions.delete_experiment_run import delete_experiment_run
from .src.functions.delete_experiment_run_batch import delete_experiment_run_batch
from .src.functions.delete_model import delete_model
from .src.functions.delete_project_file import delete_project_file
from .src.functions.get_application import get_application
from .src.functions.get_experiment import get_experiment
from .src.functions.get_experiment_run import get_experiment_run
from .src.functions.get_job import get_job
from .src.functions.get_job_run import get_job_run
from .src.functions.get_model import get_model
from .src.functions.get_model_build import get_model_build
from .src.functions.get_model_deployment import get_model_deployment
from .src.functions.list_applications import list_applications
from .src.functions.list_experiments import list_experiments
from .src.functions.list_job_runs import list_job_runs
from .src.functions.list_models import list_models
from .src.functions.list_model_builds import list_model_builds
from .src.functions.list_model_deployments import list_model_deployments
from .src.functions.list_project_files import list_project_files
from .src.functions.log_experiment_run_batch import log_experiment_run_batch
from .src.functions.restart_application import restart_application
from .src.functions.stop_application import stop_application
from .src.functions.stop_job_run import stop_job_run
from .src.functions.stop_model_deployment import stop_model_deployment
from .src.functions.update_application import update_application
from .src.functions.update_experiment import update_experiment
from .src.functions.update_experiment_run import update_experiment_run
from .src.functions.update_job import update_job
from .src.functions.update_project import update_project
from .src.functions.update_project_file_metadata import update_project_file_metadata
from .src.functions.list_runtimes import list_runtimes
from .src.functions.list_runtime_addons import list_runtime_addons
from .src.functions.list_runtime_repos import list_runtime_repos
from .src.functions.create_runtime_repo import create_runtime_repo
from .src.functions.delete_runtime_repo import delete_runtime_repo
from .src.functions.update_runtime_repo import update_runtime_repo
from .src.functions.register_custom_runtime import register_custom_runtime
from .src.functions.update_runtime_status import update_runtime_status
from .src.functions.update_runtime_addon_status import update_runtime_addon_status
from .src.functions.list_docker_credentials import list_docker_credentials
from .src.functions.create_docker_credential import create_docker_credential
from .src.functions.delete_docker_credential import delete_docker_credential
from .src.functions.set_docker_credential import set_docker_credential
from .src.functions.list_v2_keys import list_v2_keys
from .src.functions.create_v2_key import create_v2_key
from .src.functions.delete_v2_key import delete_v2_key
from .src.functions.delete_v2_keys import delete_v2_keys
from .src.functions.validate_api_key import validate_api_key
from .src.functions.list_cpu_profiles import list_cpu_profiles
from .src.functions.list_groups_quota import list_groups_quota
from .src.functions.list_users_quota import list_users_quota
from .src.functions.list_teams_accelerator_quota import list_teams_accelerator_quota
from .src.functions.list_teams import list_teams
from .src.functions.list_users_accelerator_quota import list_users_accelerator_quota
from .src.functions.list_usage import list_usage
from .src.functions.list_news_feeds import list_news_feeds
from .src.functions.list_ml_serving_apps import list_ml_serving_apps
from .src.functions.list_workload_executions import list_workload_executions
from .src.functions.list_workload_status import list_workload_status
from .src.functions.list_workload_types import list_workload_types
from .src.functions.get_default_quota import get_default_quota
from .src.functions.get_default_quotas import get_default_quotas
from .src.functions.list_all_resource_groups import list_all_resource_groups
from .src.functions.list_all_accelerator_node_labels import list_all_accelerator_node_labels


def get_config() -> Dict[str, str]:
    """Get configuration from Docker secrets or environment variables."""
    
    def read_secret_or_env(secret_name: str, env_var: str) -> str:
        secret_file = f"/run/secrets/{secret_name}"
        if os.path.exists(secret_file):
            with open(secret_file, 'r') as f:
                return f.read().strip()
        return os.environ.get(env_var, "")
    
    return {
        "host": read_secret_or_env("cai_workbench_host", "CAI_WORKBENCH_HOST"),
        "api_key": read_secret_or_env("cai_workbench_api_key", "CAI_WORKBENCH_API_KEY"),
        "project_id": read_secret_or_env("cai_workbench_project_id", "CAI_WORKBENCH_PROJECT_ID"),
        "team": read_secret_or_env("cai_workbench_team", "CAI_WORKBENCH_TEAM"),
    }


# Initialize FastMCP server for HTTP
mcp = FastMCP("cloudera-ml-http")




# --- Tools previously in TOOL_IMPLEMENTATIONS (now proper @mcp.tool) ---

@mcp.tool()
def upload_folder_tool(folder_path: str, ignore_folders: str = None, project_id: str = None) -> str:
    """Upload a folder to Cloudera AI."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(upload_folder(config, {
        "folder_path": folder_path,
        "ignore_folders": ignore_folders.split(",") if ignore_folders else None
    }), indent=2)

@mcp.tool()
def upload_file_tool(file_path: str, target_name: str = None, target_dir: str = None, project_id: str = None) -> str:
    """Upload a single file to Cloudera AI."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(upload_file(config, {
        "file_path": file_path, "target_name": target_name, "target_dir": target_dir
    }), indent=2)

@mcp.tool()
def create_job_tool(name: str, script: str, kernel: str = "python3", cpu: int = 1, memory: int = 1, nvidia_gpu: int = 0, runtime_identifier: str = None, project_id: str = None) -> str:
    """Create a new Cloudera AI job."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(create_job(config, {
        "name": name, "script": script, "kernel": kernel,
        "cpu": cpu, "memory": memory, "nvidia_gpu": nvidia_gpu,
        "runtime_identifier": runtime_identifier
    }), indent=2)

@mcp.tool()
def list_jobs_tool(project_id: str = None) -> str:
    """List all jobs in the Cloudera AI project."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(list_jobs(config, {}), indent=2)

@mcp.tool()
def get_job_tool(job_id: str, project_id: str = None) -> str:
    """Get details of a specific job."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(get_job(config, {"job_id": job_id}), indent=2)

@mcp.tool()
def update_job_tool(job_id: str, name: str = None, script: str = None, kernel: str = None, cpu: int = None, memory: int = None, nvidia_gpu: int = None, runtime_identifier: str = None, project_id: str = None) -> str:
    """Update an existing job."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    p = {"job_id": job_id}
    for k, v in {"name": name, "script": script, "kernel": kernel, "cpu": cpu, "memory": memory, "nvidia_gpu": nvidia_gpu, "runtime_identifier": runtime_identifier}.items():
        if v is not None:
            p[k] = v
    return json.dumps(update_job(config, p), indent=2)

@mcp.tool()
def delete_job_tool(job_id: str, project_id: str = None) -> str:
    """Delete a job by ID."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(delete_job(config, {"job_id": job_id}), indent=2)

@mcp.tool()
def delete_all_jobs_tool(project_id: str = None) -> str:
    """Delete all jobs in the project."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(delete_all_jobs(config, {}), indent=2)

@mcp.tool()
def get_project_id_tool(project_name: str) -> str:
    """Get project ID from a project name. Use '*' to list all."""
    config = get_config()
    return json.dumps(get_project_id(config, {"project_name": project_name}), indent=2)

@mcp.tool()
def list_projects_tool() -> str:
    """List all available projects."""
    config = get_config()
    return json.dumps(get_project_id(config, {"project_name": "*"}), indent=2)

@mcp.tool()
def create_job_run_tool(project_id: str, job_id: str, runtime_identifier: str = None, environment_variables: str = None, override_config: str = None) -> str:
    """Create a run for an existing job."""
    config = get_config()
    return json.dumps(create_job_run(config, {
        "project_id": project_id, "job_id": job_id,
        "runtime_identifier": runtime_identifier,
        "environment_variables": environment_variables,
        "override_config": override_config
    }), indent=2)

@mcp.tool()
def list_job_runs_tool(project_id: str = None, job_id: str = None) -> str:
    """List job runs."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    p = {}
    if job_id:
        p["job_id"] = job_id
    return json.dumps(list_job_runs(config, p), indent=2)

@mcp.tool()
def get_job_run_tool(job_id: str, run_id: str, project_id: str = None) -> str:
    """Get details of a job run."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(get_job_run(config, {"job_id": job_id, "run_id": run_id}), indent=2)

@mcp.tool()
def stop_job_run_tool(job_id: str, run_id: str, project_id: str = None) -> str:
    """Stop a running job run."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(stop_job_run(config, {"job_id": job_id, "run_id": run_id}), indent=2)

@mcp.tool()
def create_experiment_tool(project_id: str, name: str, description: str = None) -> str:
    """Create a new experiment."""
    config = get_config()
    return json.dumps(create_experiment(config, {"project_id": project_id, "name": name, "description": description}), indent=2)

@mcp.tool()
def list_experiments_tool(project_id: str = None) -> str:
    """List experiments in a project."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(list_experiments(config, {"project_id": project_id or config.get("project_id", "")}), indent=2)

@mcp.tool()
def get_experiment_tool(experiment_id: str, project_id: str = None) -> str:
    """Get experiment details."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(get_experiment(config, {"experiment_id": experiment_id}), indent=2)

@mcp.tool()
def update_experiment_tool(experiment_id: str, name: str = None, description: str = None, project_id: str = None) -> str:
    """Update an experiment."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(update_experiment(config, {"experiment_id": experiment_id, "name": name, "description": description}), indent=2)

@mcp.tool()
def delete_experiment_tool(experiment_id: str, project_id: str = None) -> str:
    """Delete an experiment."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(delete_experiment(config, {"experiment_id": experiment_id}), indent=2)

@mcp.tool()
def create_experiment_run_tool(project_id: str, experiment_id: str, name: str = None, description: str = None, metrics: str = None, parameters: str = None, tags: str = None) -> str:
    """Create an experiment run."""
    config = get_config()
    return json.dumps(create_experiment_run(config, {
        "project_id": project_id, "experiment_id": experiment_id,
        "name": name, "description": description, "metrics": metrics,
        "parameters": parameters, "tags": tags
    }), indent=2)

@mcp.tool()
def get_experiment_run_tool(experiment_id: str, run_id: str, project_id: str = None) -> str:
    """Get experiment run details."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(get_experiment_run(config, {"experiment_id": experiment_id, "run_id": run_id}), indent=2)

@mcp.tool()
def update_experiment_run_tool(experiment_id: str, run_id: str, name: str = None, description: str = None, metrics: str = None, parameters: str = None, tags: str = None, project_id: str = None) -> str:
    """Update an experiment run."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(update_experiment_run(config, {
        "experiment_id": experiment_id, "run_id": run_id,
        "name": name, "description": description, "metrics": metrics,
        "parameters": parameters, "tags": tags
    }), indent=2)

@mcp.tool()
def delete_experiment_run_tool(experiment_id: str, run_id: str, project_id: str = None) -> str:
    """Delete an experiment run."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(delete_experiment_run(config, {"experiment_id": experiment_id, "run_id": run_id}), indent=2)

@mcp.tool()
def delete_experiment_run_batch_tool(experiment_id: str, run_ids: str, project_id: str = None) -> str:
    """Delete multiple experiment runs."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(delete_experiment_run_batch(config, {"experiment_id": experiment_id, "run_ids": run_ids}), indent=2)

@mcp.tool()
def log_experiment_run_batch_tool(experiment_id: str, run_updates: str, project_id: str = None) -> str:
    """Log metrics/params for multiple experiment runs."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(log_experiment_run_batch(config, {"experiment_id": experiment_id, "run_updates": run_updates}), indent=2)

@mcp.tool()
def create_model_build_tool(project_id: str, model_id: str, file_path: str, function_name: str, kernel: str = "python3", runtime_identifier: str = None, cpu: int = 1, memory: int = 2, nvidia_gpu: int = 0) -> str:
    """Create a new model build."""
    config = get_config()
    return json.dumps(create_model_build(config, {
        "project_id": project_id, "model_id": model_id,
        "file_path": file_path, "function_name": function_name,
        "kernel": kernel, "runtime_identifier": runtime_identifier,
        "cpu": cpu, "memory": memory, "nvidia_gpu": nvidia_gpu
    }), indent=2)

@mcp.tool()
def create_model_deployment_tool(project_id: str, model_id: str, build_id: str, name: str, cpu: int = 1, memory: int = 2, nvidia_gpu: int = 0, replica_count: int = 1) -> str:
    """Create a new model deployment."""
    config = get_config()
    return json.dumps(create_model_deployment(config, {
        "project_id": project_id, "model_id": model_id, "build_id": build_id,
        "name": name, "cpu": cpu, "memory": memory, "nvidia_gpu": nvidia_gpu,
        "replica_count": replica_count
    }), indent=2)

@mcp.tool()
def list_models_tool(project_id: str = None) -> str:
    """List models in a project."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(list_models(config, {}), indent=2)

@mcp.tool()
def list_model_builds_tool(project_id: str = None, model_id: str = None) -> str:
    """List model builds."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    p = {}
    if model_id:
        p["model_id"] = model_id
    return json.dumps(list_model_builds(config, p), indent=2)

@mcp.tool()
def list_model_deployments_tool(project_id: str = None, model_id: str = None) -> str:
    """List model deployments."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    p = {}
    if model_id:
        p["model_id"] = model_id
    return json.dumps(list_model_deployments(config, p), indent=2)

@mcp.tool()
def get_model_tool(model_id: str, project_id: str = None) -> str:
    """Get model details."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(get_model(config, {"model_id": model_id}), indent=2)

@mcp.tool()
def get_model_build_tool(model_id: str, build_id: str, project_id: str = None) -> str:
    """Get model build details."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(get_model_build(config, {"model_id": model_id, "build_id": build_id}), indent=2)

@mcp.tool()
def get_model_deployment_tool(model_id: str, deployment_id: str, project_id: str = None) -> str:
    """Get model deployment details."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(get_model_deployment(config, {"model_id": model_id, "deployment_id": deployment_id}), indent=2)

@mcp.tool()
def stop_model_deployment_tool(model_id: str, deployment_id: str, project_id: str = None) -> str:
    """Stop a model deployment."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(stop_model_deployment(config, {"model_id": model_id, "deployment_id": deployment_id}), indent=2)

@mcp.tool()
def delete_model_tool(model_id: str, project_id: str = None) -> str:
    """Delete a model."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(delete_model(config, {"model_id": model_id}), indent=2)

@mcp.tool()
def create_application_tool(project_id: str, name: str, script: str, cpu: int = 1, memory: int = 1, nvidia_gpu: int = 0, runtime_identifier: str = None, subdomain: str = None) -> str:
    """Create a new application."""
    config = get_config()
    return json.dumps(create_application(config, {
        "project_id": project_id, "name": name, "script": script,
        "cpu": cpu, "memory": memory, "nvidia_gpu": nvidia_gpu,
        "runtime_identifier": runtime_identifier, "subdomain": subdomain
    }), indent=2)

@mcp.tool()
def list_applications_tool(project_id: str = None) -> str:
    """List applications in a project."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(list_applications(config, {}), indent=2)

@mcp.tool()
def get_application_tool(application_id: str, project_id: str = None) -> str:
    """Get application details."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(get_application(config, {"application_id": application_id}), indent=2)

@mcp.tool()
def update_application_tool(application_id: str, name: str = None, script: str = None, cpu: int = None, memory: int = None, nvidia_gpu: int = None, runtime_identifier: str = None, project_id: str = None) -> str:
    """Update an application."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    p = {"application_id": application_id}
    for k, v in {"name": name, "script": script, "cpu": cpu, "memory": memory, "nvidia_gpu": nvidia_gpu, "runtime_identifier": runtime_identifier}.items():
        if v is not None:
            p[k] = v
    return json.dumps(update_application(config, p), indent=2)

@mcp.tool()
def restart_application_tool(application_id: str, project_id: str = None) -> str:
    """Restart an application."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(restart_application(config, {"application_id": application_id}), indent=2)

@mcp.tool()
def stop_application_tool(application_id: str, project_id: str = None) -> str:
    """Stop an application."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(stop_application(config, {"application_id": application_id}), indent=2)

@mcp.tool()
def delete_application_tool(application_id: str, project_id: str = None) -> str:
    """Delete an application."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(delete_application(config, {"application_id": application_id}), indent=2)

@mcp.tool()
def list_project_files_tool(project_id: str, path: str = "") -> str:
    """List files in a project."""
    config = get_config()
    return json.dumps(list_project_files(config, {"project_id": project_id, "path": path}), indent=2)

@mcp.tool()
def delete_project_file_tool(file_path: str, project_id: str = None) -> str:
    """Delete a file from a project."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(delete_project_file(config, {"file_path": file_path}), indent=2)

@mcp.tool()
def update_project_file_metadata_tool(file_path: str, description: str = None, hidden: bool = None, project_id: str = None) -> str:
    """Update file metadata."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    return json.dumps(update_project_file_metadata(config, {"file_path": file_path, "description": description, "hidden": hidden}), indent=2)

@mcp.tool()
def update_project_tool(project_id: str = None, name: str = None, summary: str = None, template: str = None, public: bool = None, disable_git_repo: bool = None) -> str:
    """Update a project."""
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    p = {}
    for k, v in {"name": name, "summary": summary, "template": template, "public": public, "disable_git_repo": disable_git_repo}.items():
        if v is not None:
            p[k] = v
    return json.dumps(update_project(config, p), indent=2)


@mcp.custom_route("/mcp-api", methods=["POST"])
async def mcp_protocol_endpoint(request):
    """Simple MCP JSON-RPC endpoint that works reliably."""
    from starlette.responses import JSONResponse
    
    try:
        data = await request.json()
        method = data.get("method", "")
        params = data.get("params", {})
        request_id = data.get("id", "unknown")
        
        if method == "initialize":
            return JSONResponse({
                "jsonrpc": "2.0", 
                "id": request_id, 
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "cloudera-ml-http",
                        "version": "2.1.0"
                    }
                }
            })
            
        elif method == "tools/list":
            # Dynamically discover all registered tools from FastMCP
            tools_dict = await mcp.get_tools()
            tools = []
            for name, tool in tools_dict.items():
                mcp_tool = tool.to_mcp_tool()
                tools.append({
                    "name": mcp_tool.name,
                    "description": mcp_tool.description or "",
                    "inputSchema": mcp_tool.inputSchema
                })
            return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}})
            
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            tools_dict = await mcp.get_tools()
            tool = tools_dict.get(tool_name)
            if not tool:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
                }, status_code=404)

            try:
                result = await tool.run(arguments)
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": str(result)}], "isError": False}
                })
            except Exception as e:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}
                })
                
        else:
            return JSONResponse({
                "jsonrpc": "2.0", 
                "id": request_id, 
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }, status_code=404)
            
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0", 
            "id": "server-error", 
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
        }, status_code=500)


@mcp.custom_route("/test", methods=["GET"])
async def test_endpoint(request):
    """Test endpoint to verify server is running."""
    from starlette.responses import JSONResponse
    return JSONResponse({
        "status": "ok",
        "message": "Cloudera AI HTTP Server is running",
        "transport": "http",
        "endpoint": "/mcp-api",
        "tools_available": len(mcp._tool_manager._tools)
    })


@mcp.custom_route("/debug/tools", methods=["GET"])
async def debug_list_tools(request):
    """List all available tools."""
    from starlette.responses import JSONResponse
    return JSONResponse({
        "status": "ok",
        "tools_count": len(mcp._tool_manager._tools),
        "tools": list((mcp._tool_manager._tools or {}).keys())
    })


@mcp.custom_route("/debug/call", methods=["POST"])
async def debug_call_tool(request):
    """Call a tool directly without MCP protocol."""
    from starlette.responses import JSONResponse
    
    try:
        data = await request.json()
        tool_name = data.get("tool")
        params = data.get("params", {})
        
        impl_func = TOOL_IMPLEMENTATIONS.get(tool_name)
        
        if not impl_func:
            return JSONResponse({
                "status": "error",
                "message": f"Tool '{tool_name}' not found",
                "available_tools": list((mcp._tool_manager._tools or {}).keys())[:10]
            }, status_code=404)
        
        result = impl_func(**params)
        
        # Try to parse as JSON if it's a string
        if isinstance(result, str):
            try:
                parsed = json.loads(result)
                return JSONResponse({
                    "status": "ok",
                    "tool": tool_name,
                    "result": parsed
                })
            except:
                return JSONResponse({
                    "status": "ok",
                    "tool": tool_name,
                    "result": result
                })
        
        return JSONResponse({
            "status": "ok",
            "tool": tool_name,
            "result": result
        })
        
    except Exception as e:
        import traceback
        return JSONResponse({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }, status_code=500)


@mcp.tool()
def create_project_tool(
    name: str,
    description: str = None,
    template: str = "blank",
    default_project_engine_type: str = "ml_runtime",
    team_name: str = None,
) -> str:
    """
    Create a new Cloudera AI project.

    Defaults to template='blank' (empty project) and ml_runtime engine type.
    Use other templates only when you need a starter project (Python, R, git, etc.).

    team_name: Team username for the project owner (CreateProjectRequest.team_name).
    Use the team username (e.g. Team1), not the display name. Falls back to CAI_WORKBENCH_TEAM.
    """
    config = get_config()

    params_dict = {"name": name, "template": template, "default_project_engine_type": default_project_engine_type}
    if description is not None:
        params_dict["description"] = description
    if team_name is not None:
        params_dict["team_name"] = team_name

    result = create_project(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def get_project_tool(project_id: str) -> str:
    """
    get_project tool.
    """
    config = get_config()
    
    params_dict = {}
    if project_id is not None:
        params_dict['project_id'] = project_id

        
    result = get_project(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_project_tool(project_id: str) -> str:
    """
    delete_project tool.
    """
    config = get_config()
    
    params_dict = {}
    if project_id is not None:
        params_dict['project_id'] = project_id

        
    result = delete_project(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_project_names_tool(search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None) -> str:
    """
    list_project_names tool.
    """
    config = get_config()
    
    params_dict = {}
    if search_filter is not None:
        params_dict['search_filter'] = search_filter
    if sort is not None:
        params_dict['sort'] = sort
    if page_size is not None:
        params_dict['page_size'] = page_size
    if page_token is not None:
        params_dict['page_token'] = page_token

        
    result = list_project_names(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_project_collaborators_tool(project_id: str, search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None) -> str:
    """
    list_project_collaborators tool.
    """
    config = get_config()
    
    params_dict = {}
    if project_id is not None:
        params_dict['project_id'] = project_id
    if search_filter is not None:
        params_dict['search_filter'] = search_filter
    if sort is not None:
        params_dict['sort'] = sort
    if page_size is not None:
        params_dict['page_size'] = page_size
    if page_token is not None:
        params_dict['page_token'] = page_token

        
    result = list_project_collaborators(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_project_collaborator_tool(project_id: str, username: str) -> str:
    """
    delete_project_collaborator tool.
    """
    config = get_config()
    
    params_dict = {}
    if project_id is not None:
        params_dict['project_id'] = project_id
    if username is not None:
        params_dict['username'] = username

        
    result = delete_project_collaborator(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def add_project_collaborator_tool(project_id: str, username: str, permission: str) -> str:
    """
    add_project_collaborator tool.
    """
    config = get_config()
    
    params_dict = {}
    if project_id is not None:
        params_dict['project_id'] = project_id
    if username is not None:
        params_dict['username'] = username
    if permission is not None:
        params_dict['permission'] = permission

        
    result = add_project_collaborator(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_all_experiments_tool(search_filter: str = None, page_size: int = None, page_token: str = None) -> str:
    """
    list_all_experiments tool.
    """
    config = get_config()
    
    params_dict = {}
    if search_filter is not None:
        params_dict['search_filter'] = search_filter
    if page_size is not None:
        params_dict['page_size'] = page_size
    if page_token is not None:
        params_dict['page_token'] = page_token

        
    result = list_all_experiments(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_experiment_runs_tool(project_id: str, experiment_id: str, search_filter: str = None, page_size: int = None, page_token: str = None, sort: str = None) -> str:
    """
    list_experiment_runs tool.
    """
    config = get_config()
    
    params_dict = {}
    if project_id is not None:
        params_dict['project_id'] = project_id
    if experiment_id is not None:
        params_dict['experiment_id'] = experiment_id
    if search_filter is not None:
        params_dict['search_filter'] = search_filter
    if page_size is not None:
        params_dict['page_size'] = page_size
    if page_token is not None:
        params_dict['page_token'] = page_token
    if sort is not None:
        params_dict['sort'] = sort

        
    result = list_experiment_runs(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def get_experiment_run_metrics_tool(project_id: str, experiment_id: str, run_id: str, metric_key: str) -> str:
    """
    get_experiment_run_metrics tool.
    """
    config = get_config()
    
    params_dict = {}
    if project_id is not None:
        params_dict['project_id'] = project_id
    if experiment_id is not None:
        params_dict['experiment_id'] = experiment_id
    if run_id is not None:
        params_dict['run_id'] = run_id
    if metric_key is not None:
        params_dict['metric_key'] = metric_key

        
    result = get_experiment_run_metrics(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_all_jobs_tool(search_filter: str = None, page_size: int = None, page_token: str = None) -> str:
    """
    list_all_jobs tool.
    """
    config = get_config()
    
    params_dict = {}
    if search_filter is not None:
        params_dict['search_filter'] = search_filter
    if page_size is not None:
        params_dict['page_size'] = page_size
    if page_token is not None:
        params_dict['page_token'] = page_token

        
    result = list_all_jobs(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_all_models_tool(search_filter: str = None, page_size: int = None, page_token: str = None) -> str:
    """
    list_all_models tool.
    """
    config = get_config()
    
    params_dict = {}
    if search_filter is not None:
        params_dict['search_filter'] = search_filter
    if page_size is not None:
        params_dict['page_size'] = page_size
    if page_token is not None:
        params_dict['page_token'] = page_token

        
    result = list_all_models(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def create_model_tool(project_id: str, name: str, description: str = None, disable_authentication: bool = None) -> str:
    """
    create_model tool.
    """
    config = get_config()
    
    params_dict = {}
    if project_id is not None:
        params_dict['project_id'] = project_id
    if name is not None:
        params_dict['name'] = name
    if description is not None:
        params_dict['description'] = description
    if disable_authentication is not None:
        params_dict['disable_authentication'] = disable_authentication

        
    result = create_model(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def update_model_tool(project_id: str, model_id: str, name: str = None, description: str = None, visibility: str = None) -> str:
    """
    update_model tool.
    """
    config = get_config()
    
    params_dict = {}
    if project_id is not None:
        params_dict['project_id'] = project_id
    if model_id is not None:
        params_dict['model_id'] = model_id
    if name is not None:
        params_dict['name'] = name
    if description is not None:
        params_dict['description'] = description
    if visibility is not None:
        params_dict['visibility'] = visibility

        
    result = update_model(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_model_build_tool(project_id: str, model_id: str, build_id: str) -> str:
    """
    delete_model_build tool.
    """
    config = get_config()
    
    params_dict = {}
    if project_id is not None:
        params_dict['project_id'] = project_id
    if model_id is not None:
        params_dict['model_id'] = model_id
    if build_id is not None:
        params_dict['build_id'] = build_id

        
    result = delete_model_build(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def restart_model_deployment_tool(project_id: str, model_id: str, build_id: str, deployment_id: str) -> str:
    """
    restart_model_deployment tool.
    """
    config = get_config()
    
    params_dict = {}
    if project_id is not None:
        params_dict['project_id'] = project_id
    if model_id is not None:
        params_dict['model_id'] = model_id
    if build_id is not None:
        params_dict['build_id'] = build_id
    if deployment_id is not None:
        params_dict['deployment_id'] = deployment_id

        
    result = restart_model_deployment(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def download_project_file_tool(project_id: str, path: str) -> str:
    """
    download_project_file tool.
    """
    config = get_config()
    
    params_dict = {}
    if project_id is not None:
        params_dict['project_id'] = project_id
    if path is not None:
        params_dict['path'] = path

        
    result = download_project_file(config, params_dict)
    return json.dumps(result, indent=2)


@mcp.tool()
def list_registered_models_tool(search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None) -> str:
    """
    list_registered_models tool.
    """
    config = get_config()
    
    params_dict = {}
    if search_filter is not None:
        params_dict['search_filter'] = search_filter
    if sort is not None:
        params_dict['sort'] = sort
    if page_size is not None:
        params_dict['page_size'] = page_size
    if page_token is not None:
        params_dict['page_token'] = page_token

        
    result = list_registered_models(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def create_registered_model_tool(project_id: str, experiment_id: str, run_id: str, model_path: str, model_name: str, tags: str = None, description: str = None, notes: str = None, visibility: str = None) -> str:
    """
    create_registered_model tool.
    """
    config = get_config()
    
    params_dict = {}
    if project_id is not None:
        params_dict['project_id'] = project_id
    if experiment_id is not None:
        params_dict['experiment_id'] = experiment_id
    if run_id is not None:
        params_dict['run_id'] = run_id
    if model_path is not None:
        params_dict['model_path'] = model_path
    if model_name is not None:
        params_dict['model_name'] = model_name
    if tags is not None:
        params_dict['tags'] = tags
    if description is not None:
        params_dict['description'] = description
    if notes is not None:
        params_dict['notes'] = notes
    if visibility is not None:
        params_dict['visibility'] = visibility

        
    result = create_registered_model(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def update_registered_model_tool(model_id: str, description: str = None, visibility: str = None, user_id: str = None) -> str:
    """
    update_registered_model tool.
    """
    config = get_config()
    
    params_dict = {}
    if model_id is not None:
        params_dict['model_id'] = model_id
    if description is not None:
        params_dict['description'] = description
    if visibility is not None:
        params_dict['visibility'] = visibility
    if user_id is not None:
        params_dict['user_id'] = user_id

        
    result = update_registered_model(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def get_registered_model_tool(model_id: str, search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None) -> str:
    """
    get_registered_model tool.
    """
    config = get_config()
    
    params_dict = {}
    if model_id is not None:
        params_dict['model_id'] = model_id
    if search_filter is not None:
        params_dict['search_filter'] = search_filter
    if sort is not None:
        params_dict['sort'] = sort
    if page_size is not None:
        params_dict['page_size'] = page_size
    if page_token is not None:
        params_dict['page_token'] = page_token

        
    result = get_registered_model(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_registered_model_tool(model_id: str) -> str:
    """
    delete_registered_model tool.
    """
    config = get_config()
    
    params_dict = {}
    if model_id is not None:
        params_dict['model_id'] = model_id

        
    result = delete_registered_model(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def update_registered_model_version_tool(model_id: str, model_version_id: str, notes: str = None, tags: str = None) -> str:
    """
    update_registered_model_version tool.
    """
    config = get_config()
    
    params_dict = {}
    if model_id is not None:
        params_dict['model_id'] = model_id
    if model_version_id is not None:
        params_dict['model_version_id'] = model_version_id
    if notes is not None:
        params_dict['notes'] = notes
    if tags is not None:
        params_dict['tags'] = tags

        
    result = update_registered_model_version(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def get_registered_model_version_tool(model_id: str, version_id: str) -> str:
    """
    get_registered_model_version tool.
    """
    config = get_config()
    
    params_dict = {}
    if model_id is not None:
        params_dict['model_id'] = model_id
    if version_id is not None:
        params_dict['version_id'] = version_id

        
    result = get_registered_model_version(config, params_dict)
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_registered_model_version_tool(model_id: str, version_id: str) -> str:
    """
    delete_registered_model_version tool.
    """
    config = get_config()
    
    params_dict = {}
    if model_id is not None:
        params_dict['model_id'] = model_id
    if version_id is not None:
        params_dict['version_id'] = version_id

        
    result = delete_registered_model_version(config, params_dict)
    return json.dumps(result, indent=2)


# --- Runtimes / credentials / global admin (same tools as stdio_server) ---
@mcp.tool()
def list_runtimes_tool(
    search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None
) -> str:
    p = {}
    if search_filter is not None:
        p["search_filter"] = search_filter
    if sort is not None:
        p["sort"] = sort
    if page_size is not None:
        p["page_size"] = page_size
    if page_token is not None:
        p["page_token"] = page_token
    return json.dumps(list_runtimes(get_config(), p), indent=2)


@mcp.tool()
def list_runtime_addons_tool(
    search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None
) -> str:
    p = {k: v for k, v in {
        "search_filter": search_filter, "sort": sort, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_runtime_addons(get_config(), p), indent=2)


@mcp.tool()
def list_runtime_repos_tool(
    search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None
) -> str:
    p = {k: v for k, v in {
        "search_filter": search_filter, "sort": sort, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_runtime_repos(get_config(), p), indent=2)


@mcp.tool()
def create_runtime_repo_tool(body_json: str) -> str:
    return json.dumps(create_runtime_repo(get_config(), {"body": json.loads(body_json)}), indent=2)


@mcp.tool()
def delete_runtime_repo_tool(runtime_repo_id: int) -> str:
    return json.dumps(delete_runtime_repo(get_config(), {"runtime_repo_id": runtime_repo_id}), indent=2)


@mcp.tool()
def update_runtime_repo_tool(runtimerepo_id: int, body_json: str) -> str:
    return json.dumps(
        update_runtime_repo(get_config(), {"runtimerepo_id": runtimerepo_id, "body": json.loads(body_json)}),
        indent=2,
    )


@mcp.tool()
def register_custom_runtime_tool(body_json: str) -> str:
    return json.dumps(register_custom_runtime(get_config(), {"body": json.loads(body_json)}), indent=2)


@mcp.tool()
def update_runtime_status_tool(body_json: str) -> str:
    return json.dumps(update_runtime_status(get_config(), {"body": json.loads(body_json)}), indent=2)


@mcp.tool()
def update_runtime_addon_status_tool(body_json: str) -> str:
    return json.dumps(update_runtime_addon_status(get_config(), {"body": json.loads(body_json)}), indent=2)


@mcp.tool()
def list_docker_credentials_tool(
    search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None
) -> str:
    p = {k: v for k, v in {
        "search_filter": search_filter, "sort": sort, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_docker_credentials(get_config(), p), indent=2)


@mcp.tool()
def create_docker_credential_tool(body_json: str) -> str:
    return json.dumps(create_docker_credential(get_config(), {"body": json.loads(body_json)}), indent=2)


@mcp.tool()
def delete_docker_credential_tool(docker_credential_id: str) -> str:
    return json.dumps(delete_docker_credential(get_config(), {"docker_credential_id": docker_credential_id}), indent=2)


@mcp.tool()
def set_docker_credential_tool(body_json: str) -> str:
    return json.dumps(set_docker_credential(get_config(), {"body": json.loads(body_json)}), indent=2)


@mcp.tool()
def list_v2_keys_tool(username: str) -> str:
    return json.dumps(list_v2_keys(get_config(), {"username": username}), indent=2)


@mcp.tool()
def create_v2_key_tool(username: str, body_json: str) -> str:
    return json.dumps(create_v2_key(get_config(), {"username": username, "body": json.loads(body_json)}), indent=2)


@mcp.tool()
def delete_v2_key_tool(username: str, key_id: str) -> str:
    return json.dumps(delete_v2_key(get_config(), {"username": username, "key_id": key_id}), indent=2)


@mcp.tool()
def delete_v2_keys_tool(username: str) -> str:
    return json.dumps(delete_v2_keys(get_config(), {"username": username}), indent=2)


@mcp.tool()
def validate_api_key_tool(body_json: str) -> str:
    return json.dumps(validate_api_key(get_config(), {"body": json.loads(body_json)}), indent=2)


@mcp.tool()
def list_cpu_profiles_tool(
    search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None
) -> str:
    p = {k: v for k, v in {
        "search_filter": search_filter, "sort": sort, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_cpu_profiles(get_config(), p), indent=2)


@mcp.tool()
def list_groups_quota_tool(
    search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None
) -> str:
    p = {k: v for k, v in {
        "search_filter": search_filter, "sort": sort, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_groups_quota(get_config(), p), indent=2)


@mcp.tool()
def list_users_quota_tool(
    search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None
) -> str:
    p = {k: v for k, v in {
        "search_filter": search_filter, "sort": sort, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_users_quota(get_config(), p), indent=2)


@mcp.tool()
def list_teams_tool(search_filter: str = None, page_size: int = None, page_token: str = None) -> str:
    p = {k: v for k, v in {
        "search_filter": search_filter, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_teams(get_config(), p), indent=2)


@mcp.tool()
def list_teams_accelerator_quota_tool(search_filter: str = None) -> str:
    p = {}
    if search_filter is not None:
        p["search_filter"] = search_filter
    return json.dumps(list_teams_accelerator_quota(get_config(), p), indent=2)


@mcp.tool()
def list_users_accelerator_quota_tool(search_filter: str = None) -> str:
    p = {}
    if search_filter is not None:
        p["search_filter"] = search_filter
    return json.dumps(list_users_accelerator_quota(get_config(), p), indent=2)


@mcp.tool()
def list_usage_tool(
    search_filter: str = None,
    sort: str = None,
    page_size: int = None,
    page_token: str = None,
    multi_column_search_filter: str = None,
    time_range_search_filter: str = None,
) -> str:
    p = {k: v for k, v in {
        "search_filter": search_filter,
        "sort": sort,
        "page_size": page_size,
        "page_token": page_token,
        "multi_column_search_filter": multi_column_search_filter,
        "time_range_search_filter": time_range_search_filter,
    }.items() if v is not None}
    return json.dumps(list_usage(get_config(), p), indent=2)


@mcp.tool()
def list_news_feeds_tool(category: str, page_size: int = None, page_token: str = None) -> str:
    p = {"category": category}
    if page_size is not None:
        p["page_size"] = page_size
    if page_token is not None:
        p["page_token"] = page_token
    return json.dumps(list_news_feeds(get_config(), p), indent=2)


@mcp.tool()
def list_ml_serving_apps_tool(force_refresh: bool = None) -> str:
    p = {}
    if force_refresh is not None:
        p["force_refresh"] = force_refresh
    return json.dumps(list_ml_serving_apps(get_config(), p), indent=2)


@mcp.tool()
def list_workload_executions_tool(
    search_filter: str = None,
    page_size: int = None,
    page_token: str = None,
    sort: str = None,
    multi_column_search_filter: str = None,
    time_range_search_filter: str = None,
) -> str:
    p = {k: v for k, v in {
        "search_filter": search_filter,
        "page_size": page_size,
        "page_token": page_token,
        "sort": sort,
        "multi_column_search_filter": multi_column_search_filter,
        "time_range_search_filter": time_range_search_filter,
    }.items() if v is not None}
    return json.dumps(list_workload_executions(get_config(), p), indent=2)


@mcp.tool()
def list_workload_status_tool() -> str:
    return json.dumps(list_workload_status(get_config(), {}), indent=2)


@mcp.tool()
def list_workload_types_tool() -> str:
    return json.dumps(list_workload_types(get_config(), {}), indent=2)


@mcp.tool()
def get_default_quota_tool(uuid: str = None) -> str:
    p = {}
    if uuid is not None:
        p["uuid"] = uuid
    return json.dumps(get_default_quota(get_config(), p), indent=2)


@mcp.tool()
def get_default_quotas_tool(uuid: str = None) -> str:
    p = {}
    if uuid is not None:
        p["uuid"] = uuid
    return json.dumps(get_default_quotas(get_config(), p), indent=2)


@mcp.tool()
def list_all_resource_groups_tool() -> str:
    return json.dumps(list_all_resource_groups(get_config(), {}), indent=2)


@mcp.tool()
def list_all_accelerator_node_labels_tool() -> str:
    return json.dumps(list_all_accelerator_node_labels(get_config(), {}), indent=2)


def main():
    """Run the HTTP server."""
    config = get_config()
    
    # Check configuration
    if not config.get("host") or not config.get("api_key"):
        print("Error: Missing required configuration")
        print("Please set CAI_WORKBENCH_HOST and CAI_WORKBENCH_API_KEY")
        return
    
    # Get host and port from environment or use defaults
    host = os.getenv("CAI_MCP_HOST", "0.0.0.0")
    port = int(os.getenv("CAI_MCP_PORT", "8000"))
    
    print("Starting Cloudera AI HTTP Server...")
    print(f"Connected to: {config['host']}")
    print(f"Tools available: {len(mcp._tool_manager._tools)}")
    print(f"Server will start on {host}:{port}")
    print("")
    print("Endpoints:")
    print(f"  - MCP Protocol: http://localhost:{port}/mcp-api")
    print(f"  - Debug tools:  http://localhost:{port}/debug/tools")
    print(f"  - Debug call:   http://localhost:{port}/debug/call")
    print(f"  - Test status:  http://localhost:{port}/test")
    print("")
    print("⚠️  WARNING: No authentication - development use only!")
    
    # Run HTTP server
    mcp.run(transport="http", host=host, port=port)


if __name__ == "__main__":
    main()
