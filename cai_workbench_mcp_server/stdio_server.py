#!/usr/bin/env python3
"""
Cloudera AI Workbench MCP STDIO Server - Clean STDIO-only implementation

This server enables LLMs to interact with Cloudera AI via API.
Uses STDIO transport for secure subprocess communication (recommended for Claude Desktop).
"""

import os
import json
import sys
from typing import Dict, Any
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all tool implementations
try:
    # Package execution (uvx, -m module)
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
    from .src.functions.generate_diag_bundle import generate_diag_bundle
    from .src.functions.get_diag_bundle_status import get_diag_bundle_status
    from .src.functions.download_diag_bundle import download_diag_bundle
    from .src.functions.health_check import health_check
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
except ImportError:
    # Direct execution (python cai_workbench_mcp_server/stdio_server.py)
    from src.functions.upload_folder import upload_folder
    from src.functions.upload_file import upload_file
    from src.functions.create_job import create_job
    from src.functions.list_jobs import list_jobs
    from src.functions.delete_job import delete_job
    from src.functions.delete_all_jobs import delete_all_jobs
    from src.functions.get_project_id import get_project_id

    from src.functions.create_job_run import create_job_run
    from src.functions.create_experiment import create_experiment
    from src.functions.create_experiment_run import create_experiment_run
    from src.functions.create_model_build import create_model_build
    from src.functions.create_model_deployment import create_model_deployment
    from src.functions.create_application import create_application
    from src.functions.list_registered_models import list_registered_models
    from src.functions.create_registered_model import create_registered_model
    from src.functions.update_registered_model import update_registered_model
    from src.functions.get_registered_model import get_registered_model
    from src.functions.delete_registered_model import delete_registered_model
    from src.functions.update_registered_model_version import update_registered_model_version
    from src.functions.get_registered_model_version import get_registered_model_version
    from src.functions.delete_registered_model_version import delete_registered_model_version
    from src.functions.list_runtimes import list_runtimes
    from src.functions.list_runtime_addons import list_runtime_addons
    from src.functions.list_runtime_repos import list_runtime_repos
    from src.functions.create_runtime_repo import create_runtime_repo
    from src.functions.delete_runtime_repo import delete_runtime_repo
    from src.functions.update_runtime_repo import update_runtime_repo
    from src.functions.register_custom_runtime import register_custom_runtime
    from src.functions.update_runtime_status import update_runtime_status
    from src.functions.update_runtime_addon_status import update_runtime_addon_status
    from src.functions.list_docker_credentials import list_docker_credentials
    from src.functions.create_docker_credential import create_docker_credential
    from src.functions.delete_docker_credential import delete_docker_credential
    from src.functions.set_docker_credential import set_docker_credential
    from src.functions.list_v2_keys import list_v2_keys
    from src.functions.create_v2_key import create_v2_key
    from src.functions.delete_v2_key import delete_v2_key
    from src.functions.delete_v2_keys import delete_v2_keys
    from src.functions.validate_api_key import validate_api_key
    from src.functions.generate_diag_bundle import generate_diag_bundle
    from src.functions.get_diag_bundle_status import get_diag_bundle_status
    from src.functions.download_diag_bundle import download_diag_bundle
    from src.functions.health_check import health_check
    from src.functions.list_cpu_profiles import list_cpu_profiles
    from src.functions.list_groups_quota import list_groups_quota
    from src.functions.list_users_quota import list_users_quota
    from src.functions.list_teams_accelerator_quota import list_teams_accelerator_quota
    from src.functions.list_teams import list_teams
    from src.functions.list_users_accelerator_quota import list_users_accelerator_quota
    from src.functions.list_usage import list_usage
    from src.functions.list_news_feeds import list_news_feeds
    from src.functions.list_ml_serving_apps import list_ml_serving_apps
    from src.functions.list_workload_executions import list_workload_executions
    from src.functions.list_workload_status import list_workload_status
    from src.functions.list_workload_types import list_workload_types
    from src.functions.get_default_quota import get_default_quota
    from src.functions.get_default_quotas import get_default_quotas
    from src.functions.list_all_resource_groups import list_all_resource_groups
    from src.functions.list_all_accelerator_node_labels import list_all_accelerator_node_labels
    from src.functions.create_project import create_project
    from src.functions.get_project import get_project
    from src.functions.delete_project import delete_project
    from src.functions.list_project_names import list_project_names
    from src.functions.list_project_collaborators import list_project_collaborators
    from src.functions.delete_project_collaborator import delete_project_collaborator
    from src.functions.add_project_collaborator import add_project_collaborator
    from src.functions.list_all_experiments import list_all_experiments
    from src.functions.list_experiment_runs import list_experiment_runs
    from src.functions.get_experiment_run_metrics import get_experiment_run_metrics
    from src.functions.list_all_jobs import list_all_jobs
    from src.functions.list_all_models import list_all_models
    from src.functions.create_model import create_model
    from src.functions.update_model import update_model
    from src.functions.delete_model_build import delete_model_build
    from src.functions.restart_model_deployment import restart_model_deployment
    from src.functions.download_project_file import download_project_file
    from src.functions.delete_application import delete_application
    from src.functions.delete_experiment import delete_experiment
    from src.functions.delete_experiment_run import delete_experiment_run
    from src.functions.delete_experiment_run_batch import delete_experiment_run_batch
    from src.functions.delete_model import delete_model
    from src.functions.delete_project_file import delete_project_file
    from src.functions.get_application import get_application
    from src.functions.get_experiment import get_experiment
    from src.functions.get_experiment_run import get_experiment_run
    from src.functions.get_job import get_job
    from src.functions.get_job_run import get_job_run
    from src.functions.get_model import get_model
    from src.functions.get_model_build import get_model_build
    from src.functions.get_model_deployment import get_model_deployment
    from src.functions.list_applications import list_applications
    from src.functions.list_experiments import list_experiments
    from src.functions.list_job_runs import list_job_runs
    from src.functions.list_models import list_models
    from src.functions.list_model_builds import list_model_builds
    from src.functions.list_model_deployments import list_model_deployments
    from src.functions.list_project_files import list_project_files
    from src.functions.log_experiment_run_batch import log_experiment_run_batch
    from src.functions.restart_application import restart_application
    from src.functions.stop_application import stop_application
    from src.functions.stop_job_run import stop_job_run
    from src.functions.stop_model_deployment import stop_model_deployment
    from src.functions.update_application import update_application
    from src.functions.update_experiment import update_experiment
    from src.functions.update_experiment_run import update_experiment_run
    from src.functions.update_job import update_job
    from src.functions.update_project import update_project
    from src.functions.update_project_file_metadata import update_project_file_metadata


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


# Initialize FastMCP server
mcp = FastMCP("cloudera-ml")

# ==============================================================================
# MCP TOOL DEFINITIONS - All 48 tools
# ==============================================================================

# File Operations
@mcp.tool()
def upload_folder_tool(folder_path: str, ignore_folders: str = None, project_id: str = None) -> str:
    """
    Upload a folder to Cloudera AI.
    
    Args:
        folder_path: Local path to the folder to upload
        ignore_folders: Comma-separated list of folders to ignore (optional)
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with upload results
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    # Convert comma-separated string to list if provided
    ignore_list = ignore_folders.split(",") if ignore_folders else None
    
    result = upload_folder(config, {
        "folder_path": folder_path,
        "ignore_folders": ignore_list
    })
    return json.dumps(result, indent=2)

@mcp.tool()
def upload_file_tool(file_path: str, target_name: str = None, target_dir: str = None, project_id: str = None) -> str:
    """
    Upload a single file to Cloudera AI.
    
    Args:
        file_path: Local path to the file to upload
        target_name: Optional name to use for the uploaded file
        target_dir: Optional directory to upload to
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with upload results
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    result = upload_file(config, {
        "file_path": file_path,
        "target_name": target_name,
        "target_dir": target_dir
    })
    return json.dumps(result, indent=2)

@mcp.tool()
def list_project_files_tool(project_id: str, path: str = "") -> str:
    """
    List files in a Cloudera AI project.
    
    Args:
        project_id: ID of the project
        path: Path to list files from (relative to project root)
    
    Returns:
        JSON string containing list of project files
    """
    config = get_config()
    config["project_id"] = project_id
    
    params = {"project_id": project_id}
    if path:
        params["path"] = path
        
    result = list_project_files(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_project_file_tool(file_path: str, project_id: str = None) -> str:
    """
    Delete a file or directory from a Cloudera AI project.
    
    Args:
        file_path: Path of the file or directory to delete (relative to project root)
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with operation result
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
        
    result = delete_project_file(config, {
        "file_path": file_path,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def update_project_file_metadata_tool(file_path: str, description: str = None,
                                     hidden: bool = None, project_id: str = None) -> str:
    """
    Update metadata of a file in a Cloudera AI project.
    
    Args:
        file_path: Path of the file relative to the project root
        description: New description for the file (optional)
        hidden: Whether the file should be hidden (optional)
        project_id: ID of the project (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with file metadata update results
    """
    config = get_config()
    params = {
        "file_path": file_path
    }
    
    if project_id:
        params["project_id"] = project_id
    elif config.get("project_id"):
        params["project_id"] = config["project_id"]
    
    # Add optional parameters if provided
    if description is not None:
        params["description"] = description
        
    if hidden is not None:
        params["hidden"] = hidden
    
    result = update_project_file_metadata(config, params)
    return json.dumps(result, indent=2)

# Job Management
@mcp.tool()
def create_job_tool(name: str, script: str, kernel: str = "python3",
                   cpu: int = 1, memory: int = 1, nvidia_gpu: int = 0,
                   runtime_identifier: str = None, project_id: str = None,
                   environment_variables: str = None) -> str:
    """
    Create a new Cloudera AI job.

    Args:
        name: Job name
        script: Script path relative to project root
        kernel: Kernel type (default: python3)
        cpu: CPU cores (default: 1)
        memory: Memory in GB (default: 1)
        nvidia_gpu: Number of GPUs (default: 0)
        runtime_identifier: Runtime environment identifier
        project_id: Project ID (optional - if not provided, uses default from configuration)
        environment_variables: JSON string of default environment variables for job runs (optional)

    Returns:
        JSON string with job creation results
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id

    params = {
        "name": name,
        "script": script,
        "kernel": kernel,
        "cpu": cpu,
        "memory": memory,
        "nvidia_gpu": nvidia_gpu,
        "runtime_identifier": runtime_identifier,
    }
    if environment_variables is not None:
        try:
            params["environment_variables"] = json.loads(environment_variables)
        except json.JSONDecodeError:
            return json.dumps({"success": False, "message": "Invalid JSON for environment_variables"})

    result = create_job(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_jobs_tool(project_id: str = None) -> str:
    """
    List all jobs in the Cloudera AI project.
    
    Args:
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of jobs
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
        
    result = list_jobs(config, {})
    return json.dumps(result, indent=2)

@mcp.tool()
def get_job_tool(job_id: str, project_id: str = None) -> str:
    """
    Get details of a specific job from a Cloudera AI project.
    
    Args:
        job_id: ID of the job to retrieve
        project_id: ID of the project containing the job (optional)
    
    Returns:
        JSON string with job details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_job(config, {
        "job_id": job_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def update_job_tool(job_id: str, name: str = None, script: str = None, 
                   kernel: str = None, cpu: int = None, memory: int = None, 
                   nvidia_gpu: int = None, runtime_identifier: str = None,
                   environment_variables: str = None, project_id: str = None) -> str:
    """
    Update an existing job in Cloudera AI.
    
    Args:
        job_id: ID of the job to update
        name: New name for the job (optional)
        script: New script path for the job (optional)
        kernel: New kernel type (optional)
        cpu: New CPU cores allocation (optional)
        memory: New memory allocation in GB (optional)
        nvidia_gpu: New GPU allocation (optional)
        runtime_identifier: New runtime identifier (optional)
        environment_variables: JSON string of environment variables (optional)
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with job update results
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {
        "job_id": job_id
    }
    
    # Add optional parameters if provided
    if name is not None:
        params["name"] = name
        
    if script is not None:
        params["script"] = script
        
    if kernel is not None:
        params["kernel"] = kernel
        
    if cpu is not None:
        params["cpu"] = cpu
        
    if memory is not None:
        params["memory"] = memory
        
    if nvidia_gpu is not None:
        params["nvidia_gpu"] = nvidia_gpu
        
    if runtime_identifier is not None:
        params["runtime_identifier"] = runtime_identifier
        
    if environment_variables is not None:
        params["environment_variables"] = json.loads(environment_variables)
    
    result = update_job(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_job_tool(job_id: str, project_id: str = None) -> str:
    """
    Delete a job by ID.
    
    Args:
        job_id: ID of the job to delete
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with delete operation results
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
        
    result = delete_job(config, {"job_id": job_id})
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_all_jobs_tool(project_id: str = None) -> str:
    """
    Delete all jobs in the project.
    
    Args:
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with delete operation results
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
        
    result = delete_all_jobs(config, {})
    return json.dumps(result, indent=2)

@mcp.tool()
def create_job_run_tool(project_id: str, job_id: str, 
                       runtime_identifier: str = None, 
                       environment_variables: str = None,
                       override_config: str = None) -> str:
    """
    Create a run for an existing job in Cloudera AI.
    
    Args:
        project_id: ID of the project containing the job
        job_id: ID of the job to run
        runtime_identifier: Runtime identifier (optional)
        environment_variables: JSON string with environment variables (optional)
        override_config: JSON string with configuration overrides (optional)
    
    Returns:
        JSON string with job run data
    """
    config = get_config()
    
    params = {
        "project_id": project_id,
        "job_id": job_id
    }
    
    # Add optional parameters if provided
    if runtime_identifier:
        params["runtime_identifier"] = runtime_identifier
    
    # Parse JSON strings into dictionaries if provided
    if environment_variables:
        try:
            params["environment_variables"] = json.loads(environment_variables)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for environment_variables"
            })
    
    if override_config:
        try:
            params["override_config"] = json.loads(override_config)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for override_config"
            })
    
    result = create_job_run(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_job_runs_tool(job_id: str = None, project_id: str = None) -> str:
    """
    List all job runs in the Cloudera AI project.
    
    Args:
        job_id: If provided, only list runs for this specific job
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of job runs
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {"project_id": project_id or config.get("project_id", "")}
    if job_id:
        params["job_id"] = job_id
        
    result = list_job_runs(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def get_job_run_tool(job_id: str, run_id: str, project_id: str = None) -> str:
    """
    Get details of a specific job run from a Cloudera AI project.
    
    Args:
        job_id: ID of the job containing the run
        run_id: ID of the job run to retrieve
        project_id: ID of the project containing the job (optional)
    
    Returns:
        JSON string with job run details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_job_run(config, {
        "job_id": job_id,
        "run_id": run_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def stop_job_run_tool(job_id: str, run_id: str, project_id: str = None) -> str:
    """
    Stop a running job run in Cloudera AI.
    
    Args:
        job_id: ID of the job
        run_id: ID of the run to stop
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string containing operation result
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {
        "job_id": job_id,
        "run_id": run_id,
        "project_id": project_id or config.get("project_id", "")
    }
        
    result = stop_job_run(config, params)
    return json.dumps(result, indent=2)

# Project Management
@mcp.tool()
def get_project_id_tool(project_name: str, include_all_projects: bool = False, include_public_projects: bool = False) -> str:
    """
    Get project ID from a project name.

    Args:
        project_name: Name of the project to find. Use "*" to list all projects.
        include_all_projects: If true, includes all workspace projects (admin) or all accessible including public ones.
        include_public_projects: If true, includes public projects the user has access to.

    Returns:
        JSON string with project information and ID
    """
    config = get_config()
    params = {"project_name": project_name}
    if include_all_projects:
        params["include_all_projects"] = True
    elif include_public_projects:
        params["include_public_projects"] = True
    result = get_project_id(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_projects_tool(include_all_projects: bool = False, include_public_projects: bool = False) -> str:
    """
    List all available projects.

    Args:
        include_all_projects: If true, includes all workspace projects (admin) or all accessible including public ones.
        include_public_projects: If true, includes public projects the user has access to.

    Returns:
        JSON string with all project information
    """
    config = get_config()
    params = {"project_name": "*"}
    if include_all_projects:
        params["include_all_projects"] = True
    elif include_public_projects:
        params["include_public_projects"] = True
    result = get_project_id(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def update_project_tool(name: str = None, summary: str = None, template: str = None,
                       public: bool = None, disable_git_repo: bool = None, 
                       project_id: str = None) -> str:
    """
    Update a project in Cloudera AI.
    
    Args:
        name: New name for the project (optional)
        summary: New summary for the project (optional)
        template: New template for the project (optional)
        public: Whether the project should be public (optional)
        disable_git_repo: Whether to disable the Git repository (optional)
        project_id: ID of the project to update (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with project update results
    """
    config = get_config()
    params = {}
    
    if project_id:
        params["project_id"] = project_id
    elif config.get("project_id"):
        params["project_id"] = config["project_id"]
    
    # Add optional parameters if provided
    if name is not None:
        params["name"] = name
        
    if summary is not None:
        params["summary"] = summary
        
    if template is not None:
        params["template"] = template
        
    if public is not None:
        params["public"] = public
        
    if disable_git_repo is not None:
        params["disable_git_repo"] = disable_git_repo
    
    result = update_project(config, params)
    return json.dumps(result, indent=2)


# Experiment Tracking
@mcp.tool()
def create_experiment_tool(project_id: str, name: str, description: str = None) -> str:
    """
    Create a new experiment in Cloudera AI.
    
    Args:
        project_id: ID of the project
        name: Name of the experiment
        description: Description of the experiment (optional)
    
    Returns:
        JSON string with experiment creation result
    """
    config = get_config()
    
    params = {
        "project_id": project_id,
        "name": name
    }
    
    if description:
        params["description"] = description
    
    result = create_experiment(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_experiments_tool(project_id: str = None) -> str:
    """
    List all experiments in the Cloudera AI project.
    
    Args:
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of experiments
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
        
    result = list_experiments(config, {"project_id": project_id or config.get("project_id", "")})
    return json.dumps(result, indent=2)

@mcp.tool()
def get_experiment_tool(experiment_id: str, project_id: str = None) -> str:
    """
    Get details of a specific experiment from a Cloudera AI project.
    
    Args:
        experiment_id: ID of the experiment to retrieve
        project_id: ID of the project containing the experiment (optional)
    
    Returns:
        JSON string with experiment details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_experiment(config, {
        "experiment_id": experiment_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def update_experiment_tool(experiment_id: str, name: str = None, 
                          description: str = None, project_id: str = None) -> str:
    """
    Update an existing experiment in Cloudera AI.
    
    Args:
        experiment_id: ID of the experiment to update
        name: New name for the experiment (optional)
        description: New description for the experiment (optional)
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with experiment update results
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {
        "experiment_id": experiment_id
    }
    
    # Add optional parameters if provided
    if name is not None:
        params["name"] = name
        
    if description is not None:
        params["description"] = description
    
    result = update_experiment(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_experiment_tool(experiment_id: str, project_id: str = None) -> str:
    """
    Delete an experiment in Cloudera AI.
    
    Args:
        experiment_id: ID of the experiment to delete
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with operation result
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = delete_experiment(config, {
        "experiment_id": experiment_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def create_experiment_run_tool(project_id: str, experiment_id: str, name: str = None, 
                              description: str = None, metrics: str = None,
                              parameters: str = None, tags: str = None) -> str:
    """
    Create a new experiment run in Cloudera AI.
    
    Args:
        project_id: ID of the project
        experiment_id: ID of the experiment for the run
        name: Name of the run (optional)
        description: Description of the run (optional)
        metrics: JSON string with metrics (optional)
        parameters: JSON string with parameters (optional)
        tags: Comma-separated list of tags (optional)
    
    Returns:
        JSON string with experiment run creation result
    """
    config = get_config()
    
    params = {
        "project_id": project_id,
        "experiment_id": experiment_id
    }
    
    # Add optional parameters if provided
    if name:
        params["name"] = name
    
    if description:
        params["description"] = description
    
    # Parse JSON strings into dictionaries if provided
    if metrics:
        try:
            params["metrics"] = json.loads(metrics)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for metrics"
            })
    
    if parameters:
        try:
            params["parameters"] = json.loads(parameters)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for parameters"
            })
    
    # Parse comma-separated tags into a list if provided
    if tags:
        params["tags"] = [tag.strip() for tag in tags.split(",")]
    
    result = create_experiment_run(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def get_experiment_run_tool(experiment_id: str, run_id: str, project_id: str = None) -> str:
    """
    Get details of a specific experiment run from a Cloudera AI project.
    
    Args:
        experiment_id: ID of the experiment containing the run
        run_id: ID of the experiment run to retrieve
        project_id: ID of the project containing the experiment (optional)
    
    Returns:
        JSON string with experiment run details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_experiment_run(config, {
        "experiment_id": experiment_id,
        "run_id": run_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def update_experiment_run_tool(experiment_id: str, run_id: str,
                              name: str = None, description: str = None,
                              metrics: str = None, parameters: str = None,
                              tags: str = None, project_id: str = None) -> str:
    """
    Update an existing experiment run in Cloudera AI.
    
    Args:
        experiment_id: ID of the experiment containing the run
        run_id: ID of the run to update
        name: New name for the run (optional)
        description: New description for the run (optional)
        metrics: JSON string with metrics to update (optional)
        parameters: JSON string with parameters to update (optional)
        tags: Comma-separated list of tags to set (optional)
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with experiment run update results
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {
        "experiment_id": experiment_id,
        "run_id": run_id
    }
    
    # Add optional parameters if provided
    if name is not None:
        params["name"] = name
        
    if description is not None:
        params["description"] = description
    
    # Parse JSON strings into dictionaries if provided
    if metrics:
        try:
            params["metrics"] = json.loads(metrics)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for metrics"
            })
    
    if parameters:
        try:
            params["parameters"] = json.loads(parameters)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for parameters"
            })
    
    # Parse comma-separated tags into a list if provided
    if tags:
        params["tags"] = [tag.strip() for tag in tags.split(",")]
    
    result = update_experiment_run(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_experiment_run_tool(experiment_id: str, run_id: str, project_id: str = None) -> str:
    """
    Delete an experiment run in Cloudera AI.
    
    Args:
        experiment_id: ID of the experiment containing the run
        run_id: ID of the experiment run to delete
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with operation result
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = delete_experiment_run(config, {
        "experiment_id": experiment_id,
        "run_id": run_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_experiment_run_batch_tool(experiment_id: str, run_ids: str, project_id: str = None) -> str:
    """
    Delete multiple experiment runs in a single request.
    
    Args:
        experiment_id: ID of the experiment containing the runs
        run_ids: Comma-separated list of run IDs to delete
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with operation result
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
        
    # Convert comma-separated string to list
    run_ids_list = [run_id.strip() for run_id in run_ids.split(",")]
    
    result = delete_experiment_run_batch(config, {
        "experiment_id": experiment_id,
        "run_ids": run_ids_list,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def log_experiment_run_batch_tool(experiment_id: str, run_updates: str, project_id: str = None) -> str:
    """
    Log metrics and parameters for multiple experiment runs in a batch.
    
    Args:
        experiment_id: ID of the experiment containing the runs
        run_updates: JSON string containing an array of run update objects, each with:
            - id: ID of the run to update
            - metrics (optional): Dictionary of metrics to log
            - parameters (optional): Dictionary of parameters to log
            - tags (optional): Array of tags to add to the run
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string containing operation result
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    # Parse the run_updates JSON string
    try:
        run_updates_list = json.loads(run_updates)
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "message": "Invalid JSON for run_updates"
        }, indent=2)
    
    params = {
        "experiment_id": experiment_id,
        "run_updates": run_updates_list,
        "project_id": project_id or config.get("project_id", "")
    }
        
    result = log_experiment_run_batch(config, params)
    return json.dumps(result, indent=2)

# Model Management
@mcp.tool()
def list_models_tool(project_id: str = None) -> str:
    """
    List all models in the Cloudera AI project.
    
    Args:
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of models
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
        
    result = list_models(config, {"project_id": project_id or config.get("project_id", "")})
    return json.dumps(result, indent=2)

@mcp.tool()
def get_model_tool(model_id: str, project_id: str = None) -> str:
    """
    Get details of a specific model from a Cloudera AI project.
    
    Args:
        model_id: ID of the model to retrieve
        project_id: ID of the project containing the model (optional)
    
    Returns:
        JSON string with model details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_model(config, {
        "model_id": model_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_model_tool(model_id: str, project_id: str = None) -> str:
    """
    Delete a model in Cloudera AI.
    
    Args:
        model_id: ID of the model to delete
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with operation result
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
        
    result = delete_model(config, {
        "model_id": model_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def create_model_build_tool(project_id: str, model_id: str, file_path: str, function_name: str,
                           kernel: str = "python3", runtime_identifier: str = None,
                           replica_size: str = None, cpu: int = 1, memory: int = 2,
                           nvidia_gpu: int = 0, use_custom_docker_image: bool = False,
                           custom_docker_image: str = None, environment_variables: str = None) -> str:
    """
    Create a new model build in Cloudera AI.
    
    Args:
        project_id: ID of the project
        model_id: ID of the model to build
        file_path: Path to the model script file or main Python file
        function_name: Name of the function that contains the model code
        kernel: Kernel type (default: python3)
        runtime_identifier: Runtime identifier (optional)
        replica_size: Pod size for the build (optional)
        cpu: CPU cores (default: 1)
        memory: Memory in GB (default: 2)
        nvidia_gpu: Number of GPUs (default: 0)
        use_custom_docker_image: Whether to use a custom Docker image (default: False)
        custom_docker_image: Custom Docker image to use (optional)
        environment_variables: JSON string with environment variables (optional)
    
    Returns:
        JSON string with model build data
    """
    config = get_config()
    
    params = {
        "project_id": project_id,
        "model_id": model_id,
        "file_path": file_path,
        "function_name": function_name,
        "kernel": kernel,
        "cpu": cpu,
        "memory": memory,
        "nvidia_gpu": nvidia_gpu,
        "use_custom_docker_image": use_custom_docker_image
    }
    
    # Add optional parameters if provided
    if runtime_identifier:
        params["runtime_identifier"] = runtime_identifier
    
    if replica_size:
        params["replica_size"] = replica_size
    
    if custom_docker_image:
        params["custom_docker_image"] = custom_docker_image
    
    # Parse JSON string into dictionary if provided
    if environment_variables:
        try:
            params["environment_variables"] = json.loads(environment_variables)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for environment_variables"
            })
    
    result = create_model_build(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_model_builds_tool(model_id: str = None, project_id: str = None) -> str:
    """
    List all model builds in the Cloudera AI project.
    
    Args:
        model_id: If provided, only list builds for this specific model
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of model builds
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {"project_id": project_id or config.get("project_id", "")}
    if model_id:
        params["model_id"] = model_id
        
    result = list_model_builds(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def get_model_build_tool(model_id: str, build_id: str, project_id: str = None) -> str:
    """
    Get details of a specific model build from a Cloudera AI project.
    
    Args:
        model_id: ID of the model that contains the build
        build_id: ID of the model build to retrieve
        project_id: ID of the project containing the model (optional)
    
    Returns:
        JSON string with model build details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_model_build(config, {
        "model_id": model_id,
        "build_id": build_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def create_model_deployment_tool(project_id: str, model_id: str, build_id: str, name: str,
                                cpu: int = 1, memory: int = 2, replica_count: int = 1,
                                min_replica_count: int = None, max_replica_count: int = None,
                                nvidia_gpu: int = 0, enable_auth: bool = True,
                                target_node_selector: str = None, environment_variables: str = None) -> str:
    """
    Create a new model deployment in Cloudera AI.
    
    Args:
        project_id: ID of the project
        model_id: ID of the model to deploy
        build_id: ID of the model build to deploy
        name: Name of the deployment
        cpu: CPU cores (default: 1)
        memory: Memory in GB (default: 2)
        replica_count: Number of replicas (default: 1)
        min_replica_count: Minimum number of replicas (optional)
        max_replica_count: Maximum number of replicas (optional)
        nvidia_gpu: Number of GPUs (default: 0)
        enable_auth: Whether to enable authentication (default: True)
        target_node_selector: Target node selector for the deployment (optional)
        environment_variables: JSON string with environment variables (optional)
    
    Returns:
        JSON string with model deployment data
    """
    config = get_config()
    
    params = {
        "project_id": project_id,
        "model_id": model_id,
        "build_id": build_id,
        "name": name,
        "cpu": cpu,
        "memory": memory,
        "replica_count": replica_count,
        "nvidia_gpu": nvidia_gpu,
        "enable_auth": enable_auth
    }
    
    # Add optional parameters if provided
    if min_replica_count is not None:
        params["min_replica_count"] = min_replica_count
    
    if max_replica_count is not None:
        params["max_replica_count"] = max_replica_count
    
    if target_node_selector:
        params["target_node_selector"] = target_node_selector
    
    # Parse JSON string into dictionary if provided
    if environment_variables:
        try:
            params["environment_variables"] = json.loads(environment_variables)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for environment_variables"
            })
    
    result = create_model_deployment(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_model_deployments_tool(model_id: str = None, build_id: str = None, project_id: str = None) -> str:
    """
    List all model deployments in the Cloudera AI project.
    
    Args:
        model_id: If provided, only list deployments for this specific model
        build_id: If provided, only list deployments for this specific build
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of model deployments
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {"project_id": project_id or config.get("project_id", "")}
    if model_id:
        params["model_id"] = model_id
    if build_id:
        params["build_id"] = build_id
        
    result = list_model_deployments(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def get_model_deployment_tool(model_id: str, deployment_id: str, project_id: str = None) -> str:
    """
    Get details of a specific model deployment from a Cloudera AI project.
    
    Args:
        model_id: ID of the model that contains the deployment
        deployment_id: ID of the model deployment to retrieve
        project_id: ID of the project containing the model (optional)
    
    Returns:
        JSON string with model deployment details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_model_deployment(config, {
        "model_id": model_id,
        "deployment_id": deployment_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def stop_model_deployment_tool(model_id: str, deployment_id: str, project_id: str = None) -> str:
    """
    Stop a model deployment in Cloudera AI.
    
    Args:
        model_id: ID of the model
        deployment_id: ID of the deployment to stop
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string containing operation result
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {
        "model_id": model_id,
        "deployment_id": deployment_id,
        "project_id": project_id or config.get("project_id", "")
    }
        
    result = stop_model_deployment(config, params)
    return json.dumps(result, indent=2)

# Application Management
@mcp.tool()
def create_application_tool(project_id: str, name: str,
                           subdomain: str = None,
                           script: str = None, kernel: str = "python3",
                           cpu: int = 1, memory: int = 1, nvidia_gpu: int = 0,
                           runtime_identifier: str = None,
                           environment_variables: str = None) -> str:
    """
    Create a new application in Cloudera AI.

    Args:
        project_id: ID of the project
        name: Name of the application
        subdomain: Subdomain for the application URL (optional, auto-generated from name if not provided)
        script: Script path relative to project root (optional)
        kernel: Kernel type (default: python3)
        cpu: CPU cores (default: 1)
        memory: Memory in GB (default: 1)
        nvidia_gpu: Number of GPUs (default: 0)
        runtime_identifier: Runtime environment identifier (optional)
        environment_variables: JSON string with environment variables (optional)

    Returns:
        JSON string with application creation result
    """
    config = get_config()

    params = {
        "project_id": project_id,
        "name": name,
        "kernel": kernel,
        "cpu": cpu,
        "memory": memory,
        "nvidia_gpu": nvidia_gpu
    }

    if subdomain:
        params["subdomain"] = subdomain
    
    if script:
        params["script"] = script
        
    if runtime_identifier:
        params["runtime_identifier"] = runtime_identifier
    
    if environment_variables:
        try:
            params["environment_variables"] = json.loads(environment_variables)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for environment_variables"
            })
    
    result = create_application(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_applications_tool(project_id: str = None) -> str:
    """
    List all applications in the Cloudera AI project.
    
    Args:
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of applications
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
        
    result = list_applications(config, {"project_id": project_id or config.get("project_id", "")})
    return json.dumps(result, indent=2)

@mcp.tool()
def get_application_tool(application_id: str, project_id: str = None) -> str:
    """
    Get details of a specific application from a Cloudera AI project.
    
    Args:
        application_id: ID of the application to get details for
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with application details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
        
    result = get_application(config, {
        "application_id": application_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def update_application_tool(application_id: str, name: str = None, 
                           script: str = None, kernel: str = None,
                           cpu: int = None, memory: int = None, 
                           nvidia_gpu: int = None, runtime_identifier: str = None,
                           environment_variables: str = None, 
                           project_id: str = None) -> str:
    """
    Update an existing application in Cloudera AI.
    
    Args:
        application_id: ID of the application to update
        name: New name for the application (optional)
        script: New script path (optional)
        kernel: New kernel type (optional)
        cpu: New CPU cores allocation (optional)
        memory: New memory allocation in GB (optional)
        nvidia_gpu: New GPU allocation (optional)
        runtime_identifier: New runtime identifier (optional)
        environment_variables: JSON string of environment variables (optional)
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with application update results
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {
        "application_id": application_id
    }
    
    # Add optional parameters if provided
    if name is not None:
        params["name"] = name
        
    if script is not None:
        params["script"] = script
        
    if kernel is not None:
        params["kernel"] = kernel
        
    if cpu is not None:
        params["cpu"] = cpu
        
    if memory is not None:
        params["memory"] = memory
        
    if nvidia_gpu is not None:
        params["nvidia_gpu"] = nvidia_gpu
        
    if runtime_identifier is not None:
        params["runtime_identifier"] = runtime_identifier
        
    if environment_variables is not None:
        try:
            params["environment_variables"] = json.loads(environment_variables)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for environment_variables"
            })
    
    result = update_application(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def restart_application_tool(application_id: str, project_id: str = None) -> str:
    """
    Restart a running application in a Cloudera AI project.
    
    Args:
        application_id: ID of the application to restart
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string containing operation result
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {
        "application_id": application_id,
        "project_id": project_id or config.get("project_id", "")
    }
        
    result = restart_application(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def stop_application_tool(application_id: str, project_id: str = None) -> str:
    """
    Stop a running application in Cloudera AI.
    
    Args:
        application_id: ID of the application to stop
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string containing operation result
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {
        "application_id": application_id,
        "project_id": project_id or config.get("project_id", "")
    }
        
    result = stop_application(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_application_tool(application_id: str, project_id: str = None) -> str:
    """
    Delete an application in Cloudera AI.
    
    Args:
        application_id: ID of the application to delete
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with operation result
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = delete_application(config, {
        "application_id": application_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)


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
    Register a model.

    Args:
        project_id: ID of the project
        experiment_id: ID of the experiment the run belongs to
        run_id: ID of the ExperimentRun (must be FINISHED with model artifacts)
        model_path: MLflow artifact path used when logging the model (e.g. "model")
        model_name: Name for the registered model
        tags: JSON array string of tags, e.g. '[{"key":"env","value":"prod"}]' (optional)
        description: Registered model description (optional)
        notes: Registered model version notes (optional)
        visibility: Model visibility - "PRIVATE" or "PUBLIC" (optional)

    Returns:
        JSON string with registered model data
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


# --- Runtimes administration ---
@mcp.tool()
def list_runtimes_tool(
    search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None
) -> str:
    """
    List available runtimes in Cloudera AI. Use search_filter to find ENABLED runtimes.

    To get only active/usable runtimes, pass: search_filter={"status":"ENABLED"}
    Supports pagination via page_size and page_token. Returns image_identifier,
    editor, kernel, edition, full_version, and status for each runtime.
    """
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
    """List runtime addons."""
    p = {k: v for k, v in {
        "search_filter": search_filter, "sort": sort, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_runtime_addons(get_config(), p), indent=2)


@mcp.tool()
def list_runtime_repos_tool(
    search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None
) -> str:
    """List runtime repos."""
    p = {k: v for k, v in {
        "search_filter": search_filter, "sort": sort, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_runtime_repos(get_config(), p), indent=2)


@mcp.tool()
def create_runtime_repo_tool(body_json: str) -> str:
    """Create runtime repo. body_json: CreateRuntimeRepoRequest as JSON object."""
    return json.dumps(create_runtime_repo(get_config(), {"body": json.loads(body_json)}), indent=2)


@mcp.tool()
def delete_runtime_repo_tool(runtime_repo_id: int) -> str:
    """Delete a runtime repo by id."""
    return json.dumps(delete_runtime_repo(get_config(), {"runtime_repo_id": runtime_repo_id}), indent=2)


@mcp.tool()
def update_runtime_repo_tool(runtimerepo_id: int, body_json: str) -> str:
    """PATCH runtime repo. body_json: fields to update."""
    return json.dumps(
        update_runtime_repo(get_config(), {"runtimerepo_id": runtimerepo_id, "body": json.loads(body_json)}),
        indent=2,
    )


@mcp.tool()
def register_custom_runtime_tool(body_json: str) -> str:
    """Register custom runtime (POST /api/v2/runtimes). body_json: RegisterCustomRuntimeRequest."""
    return json.dumps(register_custom_runtime(get_config(), {"body": json.loads(body_json)}), indent=2)


@mcp.tool()
def update_runtime_status_tool(body_json: str) -> str:
    """Update runtime status (POST runtimes:update)."""
    return json.dumps(update_runtime_status(get_config(), {"body": json.loads(body_json)}), indent=2)


@mcp.tool()
def update_runtime_addon_status_tool(body_json: str) -> str:
    """Update runtime addon status."""
    return json.dumps(update_runtime_addon_status(get_config(), {"body": json.loads(body_json)}), indent=2)


# --- Access & credentials ---
@mcp.tool()
def list_docker_credentials_tool(
    search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None
) -> str:
    """List Docker registry credentials."""
    p = {k: v for k, v in {
        "search_filter": search_filter, "sort": sort, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_docker_credentials(get_config(), p), indent=2)


@mcp.tool()
def create_docker_credential_tool(body_json: str) -> str:
    """Create Docker credential."""
    return json.dumps(create_docker_credential(get_config(), {"body": json.loads(body_json)}), indent=2)


@mcp.tool()
def delete_docker_credential_tool(docker_credential_id: str) -> str:
    """Delete a Docker credential by id."""
    return json.dumps(delete_docker_credential(get_config(), {"docker_credential_id": docker_credential_id}), indent=2)


@mcp.tool()
def set_docker_credential_tool(body_json: str) -> str:
    """Set Docker credential for runtime (runtimes/credential:set)."""
    return json.dumps(set_docker_credential(get_config(), {"body": json.loads(body_json)}), indent=2)


@mcp.tool()
def list_v2_keys_tool(username: str) -> str:
    """List API v2 keys for a user."""
    return json.dumps(list_v2_keys(get_config(), {"username": username}), indent=2)


@mcp.tool()
def create_v2_key_tool(username: str, body_json: str) -> str:
    """Create API v2 key."""
    return json.dumps(create_v2_key(get_config(), {"username": username, "body": json.loads(body_json)}), indent=2)


@mcp.tool()
def delete_v2_key_tool(username: str, key_id: str) -> str:
    """Delete one API v2 key."""
    return json.dumps(delete_v2_key(get_config(), {"username": username, "key_id": key_id}), indent=2)


@mcp.tool()
def delete_v2_keys_tool(username: str) -> str:
    """Delete all API v2 keys for a user."""
    return json.dumps(delete_v2_keys(get_config(), {"username": username}), indent=2)


@mcp.tool()
def validate_api_key_tool(body_json: str) -> str:
    """Validate API v2 key (POST /api/v2/auth/validate_key)."""
    return json.dumps(validate_api_key(get_config(), {"body": json.loads(body_json)}), indent=2)


# --- Global listings & admin ---
@mcp.tool()
def list_cpu_profiles_tool(
    search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None
) -> str:
    """List CPU profiles."""
    p = {k: v for k, v in {
        "search_filter": search_filter, "sort": sort, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_cpu_profiles(get_config(), p), indent=2)


@mcp.tool()
def list_groups_quota_tool(
    search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None
) -> str:
    """List groups and quotas (admin)."""
    p = {k: v for k, v in {
        "search_filter": search_filter, "sort": sort, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_groups_quota(get_config(), p), indent=2)


@mcp.tool()
def list_users_quota_tool(
    search_filter: str = None, sort: str = None, page_size: int = None, page_token: str = None
) -> str:
    """List users and quotas (admin)."""
    p = {k: v for k, v in {
        "search_filter": search_filter, "sort": sort, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_users_quota(get_config(), p), indent=2)


@mcp.tool()
def list_teams_tool(search_filter: str = None, page_size: int = None, page_token: str = None) -> str:
    """List team usernames for create_project_tool team_name (CreateProjectRequest.team_name)."""
    p = {k: v for k, v in {
        "search_filter": search_filter, "page_size": page_size, "page_token": page_token
    }.items() if v is not None}
    return json.dumps(list_teams(get_config(), p), indent=2)


@mcp.tool()
def list_teams_accelerator_quota_tool(search_filter: str = None) -> str:
    """List team accelerator quota."""
    p = {}
    if search_filter is not None:
        p["search_filter"] = search_filter
    return json.dumps(list_teams_accelerator_quota(get_config(), p), indent=2)


@mcp.tool()
def list_users_accelerator_quota_tool(search_filter: str = None) -> str:
    """List user accelerator quota."""
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
    """List workspace usage (admin view)."""
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
    """List news feeds for a category."""
    p = {"category": category}
    if page_size is not None:
        p["page_size"] = page_size
    if page_token is not None:
        p["page_token"] = page_token
    return json.dumps(list_news_feeds(get_config(), p), indent=2)


@mcp.tool()
def list_ml_serving_apps_tool(force_refresh: bool = None) -> str:
    """List ML Serving apps."""
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
    """List workload executions."""
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
    """List workload status enum values."""
    return json.dumps(list_workload_status(get_config(), {}), indent=2)


@mcp.tool()
def list_workload_types_tool() -> str:
    """List workload types."""
    return json.dumps(list_workload_types(get_config(), {}), indent=2)


@mcp.tool()
def get_default_quota_tool(uuid: str = None) -> str:
    """Get default user quota (optional uuid query)."""
    p = {}
    if uuid is not None:
        p["uuid"] = uuid
    return json.dumps(get_default_quota(get_config(), p), indent=2)


@mcp.tool()
def get_default_quotas_tool(uuid: str = None) -> str:
    """Get all default quotas."""
    p = {}
    if uuid is not None:
        p["uuid"] = uuid
    return json.dumps(get_default_quotas(get_config(), p), indent=2)


@mcp.tool()
def list_all_resource_groups_tool() -> str:
    """List resource groups."""
    return json.dumps(list_all_resource_groups(get_config(), {}), indent=2)


@mcp.tool()
def list_all_accelerator_node_labels_tool() -> str:
    """List accelerator node labels."""
    return json.dumps(list_all_accelerator_node_labels(get_config(), {}), indent=2)


@mcp.tool()
def health_check_tool() -> str:
    """Check connectivity and authentication to Cloudera AI Workbench.

    Returns:
        JSON string with status HEALTHY or UNHEALTHY and connection details
    """
    return json.dumps(health_check(get_config(), {}), indent=2)


@mcp.tool()
def generate_diag_bundle_tool(start_time: str = None, end_time: str = None) -> str:
    """Generate a diagnostics bundle for the Cloudera AI Workbench.

    Initiates bundle generation and returns a request_id.
    Use get_diag_bundle_status_tool to poll for completion, then
    download_diag_bundle_tool to retrieve the bundle.

    Args:
        start_time: Start time for diagnostics collection (optional)
        end_time: End time for diagnostics collection (optional)

    Returns:
        JSON string with request_id and initial status
    """
    params = {}
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    return json.dumps(generate_diag_bundle(get_config(), params), indent=2)


@mcp.tool()
def get_diag_bundle_status_tool(request_id: str) -> str:
    """Get the status of a diagnostics bundle generation request.

    Status values: DIAG_IN_PROGRESS, DIAG_COMPLETED, DIAG_FAILED, DIAG_NOT_STARTED

    Args:
        request_id: The request ID returned by generate_diag_bundle_tool

    Returns:
        JSON string with status and timing information
    """
    return json.dumps(get_diag_bundle_status(get_config(), {"request_id": request_id}), indent=2)


@mcp.tool()
def download_diag_bundle_tool(request_id: str) -> str:
    """Download a completed diagnostics bundle.

    The bundle must have status DIAG_COMPLETED. Check with
    get_diag_bundle_status_tool before calling this.

    Args:
        request_id: The request ID of the completed diagnostics bundle

    Returns:
        JSON string with download result
    """
    return json.dumps(download_diag_bundle(get_config(), {"request_id": request_id}), indent=2)


def main():
    """Main entry point for the Cloudera AI Workbench MCP STDIO server."""
    # Check required configuration
    config = get_config()
    required_config = ["host", "api_key"]
    missing = [k for k in required_config if not config.get(k)]
    
    if missing:
        print(f"Error: Missing required configuration: {', '.join(missing)}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please set the following environment variables:", file=sys.stderr)
        print("  CAI_WORKBENCH_HOST=https://ml-xxxx.cloudera.site", file=sys.stderr)
        print("  CAI_WORKBENCH_API_KEY=your-api-key", file=sys.stderr)
        print("  CAI_WORKBENCH_PROJECT_ID=your-project-id  # Optional", file=sys.stderr)
        exit(1)
    
    # For STDIO, only log to stderr
    print(f"Starting Cloudera AI Workbench MCP Server (STDIO mode)...", file=sys.stderr)
    print(f"Connected to: {config['host']}", file=sys.stderr)
    print("105 tools available", file=sys.stderr)
    print("🔒 Secure Transport: Using environment variables for authentication", file=sys.stderr)
    
    # Run STDIO server (default transport)
    mcp.run()


if __name__ == "__main__":
    main()
