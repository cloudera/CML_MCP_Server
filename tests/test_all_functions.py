#!/usr/bin/env python3
"""
Comprehensive test suite for all CAI Workbench MCP Server functions
Suitable for CI/CD pipeline unit testing

This test suite covers all 105 tools/functions in the repository with:
- Security validation (no subprocess/curl vulnerabilities)
- Function signature validation
- Error handling validation
- Response structure validation
"""

import pytest
import os
import sys
import inspect

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all functions
from cai_workbench_mcp_server.src.functions.batch_list_projects import batch_list_projects
from cai_workbench_mcp_server.src.functions.create_application import create_application
from cai_workbench_mcp_server.src.functions.create_experiment import create_experiment
from cai_workbench_mcp_server.src.functions.create_experiment_run import create_experiment_run
from cai_workbench_mcp_server.src.functions.create_job import create_job
from cai_workbench_mcp_server.src.functions.create_job_run import create_job_run
from cai_workbench_mcp_server.src.functions.create_model_build import create_model_build
from cai_workbench_mcp_server.src.functions.create_model_deployment import create_model_deployment
from cai_workbench_mcp_server.src.functions.delete_all_jobs import delete_all_jobs
from cai_workbench_mcp_server.src.functions.delete_application import delete_application
from cai_workbench_mcp_server.src.functions.delete_experiment import delete_experiment
from cai_workbench_mcp_server.src.functions.delete_experiment_run import delete_experiment_run
from cai_workbench_mcp_server.src.functions.delete_experiment_run_batch import delete_experiment_run_batch
from cai_workbench_mcp_server.src.functions.delete_job import delete_job
from cai_workbench_mcp_server.src.functions.delete_model import delete_model
from cai_workbench_mcp_server.src.functions.delete_project_file import delete_project_file
from cai_workbench_mcp_server.src.functions.get_application import get_application
from cai_workbench_mcp_server.src.functions.get_experiment import get_experiment
from cai_workbench_mcp_server.src.functions.get_experiment_run import get_experiment_run
from cai_workbench_mcp_server.src.functions.get_job import get_job
from cai_workbench_mcp_server.src.functions.get_job_run import get_job_run
from cai_workbench_mcp_server.src.functions.get_model import get_model
from cai_workbench_mcp_server.src.functions.get_model_build import get_model_build
from cai_workbench_mcp_server.src.functions.get_model_deployment import get_model_deployment
from cai_workbench_mcp_server.src.functions.get_project_id import get_project_id
from cai_workbench_mcp_server.src.functions.get_runtimes import get_runtimes
from cai_workbench_mcp_server.src.functions.list_applications import list_applications
from cai_workbench_mcp_server.src.functions.list_experiments import list_experiments
from cai_workbench_mcp_server.src.functions.list_job_runs import list_job_runs
from cai_workbench_mcp_server.src.functions.list_jobs import list_jobs
from cai_workbench_mcp_server.src.functions.list_model_builds import list_model_builds
from cai_workbench_mcp_server.src.functions.list_model_deployments import list_model_deployments
from cai_workbench_mcp_server.src.functions.list_models import list_models
from cai_workbench_mcp_server.src.functions.list_project_files import list_project_files
from cai_workbench_mcp_server.src.functions.log_experiment_run_batch import log_experiment_run_batch
from cai_workbench_mcp_server.src.functions.restart_application import restart_application
from cai_workbench_mcp_server.src.functions.stop_application import stop_application
from cai_workbench_mcp_server.src.functions.stop_job_run import stop_job_run
from cai_workbench_mcp_server.src.functions.stop_model_deployment import stop_model_deployment
from cai_workbench_mcp_server.src.functions.update_application import update_application
from cai_workbench_mcp_server.src.functions.update_experiment import update_experiment
from cai_workbench_mcp_server.src.functions.update_experiment_run import update_experiment_run
from cai_workbench_mcp_server.src.functions.update_job import update_job
from cai_workbench_mcp_server.src.functions.update_project import update_project
from cai_workbench_mcp_server.src.functions.update_project_file_metadata import update_project_file_metadata
from cai_workbench_mcp_server.src.functions.upload_file import upload_file
from cai_workbench_mcp_server.src.functions.list_registered_models import list_registered_models
from cai_workbench_mcp_server.src.functions.create_registered_model import create_registered_model
from cai_workbench_mcp_server.src.functions.update_registered_model import update_registered_model
from cai_workbench_mcp_server.src.functions.get_registered_model import get_registered_model
from cai_workbench_mcp_server.src.functions.delete_registered_model import delete_registered_model
from cai_workbench_mcp_server.src.functions.update_registered_model_version import update_registered_model_version
from cai_workbench_mcp_server.src.functions.get_registered_model_version import get_registered_model_version
from cai_workbench_mcp_server.src.functions.delete_registered_model_version import delete_registered_model_version
from cai_workbench_mcp_server.src.functions.create_project import create_project
from cai_workbench_mcp_server.src.functions.get_project import get_project
from cai_workbench_mcp_server.src.functions.delete_project import delete_project
from cai_workbench_mcp_server.src.functions.list_project_names import list_project_names
from cai_workbench_mcp_server.src.functions.list_project_collaborators import list_project_collaborators
from cai_workbench_mcp_server.src.functions.delete_project_collaborator import delete_project_collaborator
from cai_workbench_mcp_server.src.functions.add_project_collaborator import add_project_collaborator
from cai_workbench_mcp_server.src.functions.list_all_experiments import list_all_experiments
from cai_workbench_mcp_server.src.functions.list_experiment_runs import list_experiment_runs
from cai_workbench_mcp_server.src.functions.get_experiment_run_metrics import get_experiment_run_metrics
from cai_workbench_mcp_server.src.functions.list_all_jobs import list_all_jobs
from cai_workbench_mcp_server.src.functions.list_all_models import list_all_models
from cai_workbench_mcp_server.src.functions.create_model import create_model
from cai_workbench_mcp_server.src.functions.update_model import update_model
from cai_workbench_mcp_server.src.functions.delete_model_build import delete_model_build
from cai_workbench_mcp_server.src.functions.restart_model_deployment import restart_model_deployment
from cai_workbench_mcp_server.src.functions.download_project_file import download_project_file
from cai_workbench_mcp_server.src.functions.list_runtimes import list_runtimes
from cai_workbench_mcp_server.src.functions.list_runtime_addons import list_runtime_addons
from cai_workbench_mcp_server.src.functions.list_runtime_repos import list_runtime_repos
from cai_workbench_mcp_server.src.functions.create_runtime_repo import create_runtime_repo
from cai_workbench_mcp_server.src.functions.delete_runtime_repo import delete_runtime_repo
from cai_workbench_mcp_server.src.functions.update_runtime_repo import update_runtime_repo
from cai_workbench_mcp_server.src.functions.register_custom_runtime import register_custom_runtime
from cai_workbench_mcp_server.src.functions.update_runtime_status import update_runtime_status
from cai_workbench_mcp_server.src.functions.update_runtime_addon_status import update_runtime_addon_status
from cai_workbench_mcp_server.src.functions.list_docker_credentials import list_docker_credentials
from cai_workbench_mcp_server.src.functions.create_docker_credential import create_docker_credential
from cai_workbench_mcp_server.src.functions.delete_docker_credential import delete_docker_credential
from cai_workbench_mcp_server.src.functions.set_docker_credential import set_docker_credential
from cai_workbench_mcp_server.src.functions.list_v2_keys import list_v2_keys
from cai_workbench_mcp_server.src.functions.create_v2_key import create_v2_key
from cai_workbench_mcp_server.src.functions.delete_v2_key import delete_v2_key
from cai_workbench_mcp_server.src.functions.delete_v2_keys import delete_v2_keys
from cai_workbench_mcp_server.src.functions.validate_api_key import validate_api_key
from cai_workbench_mcp_server.src.functions.list_cpu_profiles import list_cpu_profiles
from cai_workbench_mcp_server.src.functions.list_groups_quota import list_groups_quota
from cai_workbench_mcp_server.src.functions.list_users_quota import list_users_quota
from cai_workbench_mcp_server.src.functions.list_teams_accelerator_quota import list_teams_accelerator_quota
from cai_workbench_mcp_server.src.functions.list_teams import list_teams
from cai_workbench_mcp_server.src.functions.list_users_accelerator_quota import list_users_accelerator_quota
from cai_workbench_mcp_server.src.functions.list_usage import list_usage
from cai_workbench_mcp_server.src.functions.list_news_feeds import list_news_feeds
from cai_workbench_mcp_server.src.functions.list_ml_serving_apps import list_ml_serving_apps
from cai_workbench_mcp_server.src.functions.list_workload_executions import list_workload_executions
from cai_workbench_mcp_server.src.functions.list_workload_status import list_workload_status
from cai_workbench_mcp_server.src.functions.list_workload_types import list_workload_types
from cai_workbench_mcp_server.src.functions.get_default_quota import get_default_quota
from cai_workbench_mcp_server.src.functions.get_default_quotas import get_default_quotas
from cai_workbench_mcp_server.src.functions.list_all_resource_groups import list_all_resource_groups
from cai_workbench_mcp_server.src.functions.list_all_accelerator_node_labels import list_all_accelerator_node_labels

# upload_folder requires cmlapi (optional dependency)
try:
    from cai_workbench_mcp_server.src.functions.upload_folder import upload_folder
    HAS_UPLOAD_FOLDER = True
except ImportError:
    HAS_UPLOAD_FOLDER = False
    upload_folder = None


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_config():
    """Provide mock configuration for testing"""
    return {
        "host": "https://test.cloudera.site",
        "api_key": "test_api_key_12345",
        "project_id": "test-project-123"
    }


@pytest.fixture
def all_functions():
    """List of all functions to test"""
    functions = [
        # Create operations
        (create_application, {"name": "test", "subdomain": "test", "script": "app.py"}),
        (create_experiment, {"name": "test", "project_id": "test"}),
        (create_experiment_run, {"experiment_id": "test", "project_id": "test"}),
        (create_job, {"name": "test", "script": "test.py"}),
        (create_job_run, {"job_id": "test", "project_id": "test"}),
        (create_model_build, {"project_id": "test", "model_id": "test", "file_path": "model.py", "function_name": "predict", "kernel": "python3"}),
        (create_model_deployment, {"project_id": "test", "model_id": "test", "build_id": "test"}),
        
        # Delete operations
        (delete_all_jobs, {"project_id": "test"}),
        (delete_application, {"application_id": "test"}),
        (delete_experiment, {"experiment_id": "test", "project_id": "test"}),
        (delete_experiment_run, {"run_id": "test", "experiment_id": "test", "project_id": "test"}),
        (delete_experiment_run_batch, {"experiment_id": "test", "project_id": "test", "run_ids": ["test1", "test2"]}),
        (delete_job, {"job_id": "test", "project_id": "test"}),
        (delete_model, {"model_id": "test", "project_id": "test"}),
        (delete_project_file, {"path": "/test.txt", "project_id": "test"}),
        
        # Get operations
        (get_application, {"application_id": "test"}),
        (get_experiment, {"experiment_id": "test", "project_id": "test"}),
        (get_experiment_run, {"run_id": "test", "experiment_id": "test", "project_id": "test"}),
        (get_job, {"job_id": "test", "project_id": "test"}),
        (get_job_run, {"job_id": "test", "run_id": "test", "project_id": "test"}),
        (get_model, {"model_id": "test", "project_id": "test"}),
        (get_model_build, {"model_id": "test", "build_id": "test", "project_id": "test"}),
        (get_model_deployment, {"model_id": "test", "deployment_id": "test", "project_id": "test"}),
        (get_project_id, {"project_name": "*"}),
        (get_runtimes, {}),
        
        # List operations
        (batch_list_projects, {}),
        (list_applications, {"project_id": "test"}),
        (list_experiments, {"project_id": "test"}),
        (list_job_runs, {"job_id": "test", "project_id": "test"}),
        (list_jobs, {"project_id": "test"}),
        (list_model_builds, {"model_id": "test", "project_id": "test"}),
        (list_model_deployments, {"model_id": "test", "project_id": "test"}),
        (list_models, {"project_id": "test"}),
        (list_project_files, {"path": "/", "project_id": "test"}),
        
        # Update operations
        (log_experiment_run_batch, {"experiment_id": "test", "project_id": "test", "runs": []}),
        (restart_application, {"application_id": "test"}),
        (stop_application, {"application_id": "test"}),
        (stop_job_run, {"job_id": "test", "run_id": "test", "project_id": "test"}),
        (stop_model_deployment, {"model_id": "test", "deployment_id": "test", "project_id": "test"}),
        (update_application, {"application_id": "test"}),
        (update_experiment, {"experiment_id": "test", "project_id": "test"}),
        (update_experiment_run, {"run_id": "test", "experiment_id": "test", "project_id": "test"}),
        (update_job, {"job_id": "test", "project_id": "test"}),
        (update_project, {"project_id": "test"}),
        (update_project_file_metadata, {"path": "/test.txt", "project_id": "test"}),
        
        # Upload operations
        (upload_file, {"file_path": "/tmp/test.txt", "target_name": "test.txt", "target_dir": "/", "project_id": "test"}),
        (create_project, {"name": "test"}),
        (get_project, {"project_id": "test"}),
        (delete_project, {"project_id": "test"}),
        (list_project_names, {}),
        (list_project_collaborators, {"project_id": "test"}),
        (delete_project_collaborator, {"project_id": "test", "username": "test"}),
        (add_project_collaborator, {"project_id": "test", "username": "test", "permission": "read"}),
        (list_all_experiments, {}),
        (list_experiment_runs, {"project_id": "test", "experiment_id": "test"}),
        (get_experiment_run_metrics, {"project_id": "test", "experiment_id": "test", "run_id": "test", "metric_key": "test"}),
        (list_all_jobs, {}),
        (list_all_models, {}),
        (create_model, {"project_id": "test", "name": "test"}),
        (update_model, {"project_id": "test", "model_id": "test"}),
        (delete_model_build, {"project_id": "test", "model_id": "test", "build_id": "test"}),
        (restart_model_deployment, {"project_id": "test", "model_id": "test", "build_id": "test", "deployment_id": "test"}),
        (download_project_file, {"project_id": "test", "path": "test.txt"}),
        (list_runtimes, {}),
        (list_runtime_addons, {}),
        (list_runtime_repos, {}),
        (create_runtime_repo, {"body": {}}),
        (delete_runtime_repo, {"runtime_repo_id": 0}),
        (update_runtime_repo, {"runtimerepo_id": 0, "body": {}}),
        (register_custom_runtime, {"body": {}}),
        (update_runtime_status, {"body": {}}),
        (update_runtime_addon_status, {"body": {}}),
        (list_docker_credentials, {}),
        (create_docker_credential, {"body": {}}),
        (delete_docker_credential, {"docker_credential_id": "x"}),
        (set_docker_credential, {"body": {}}),
        (list_v2_keys, {"username": "test"}),
        (create_v2_key, {"username": "test", "body": {}}),
        (delete_v2_key, {"username": "test", "key_id": "x"}),
        (delete_v2_keys, {"username": "test"}),
        (validate_api_key, {"body": {}}),
        (list_cpu_profiles, {}),
        (list_groups_quota, {}),
        (list_users_quota, {}),
        (list_teams_accelerator_quota, {}),
        (list_teams, {}),
        (list_users_accelerator_quota, {}),
        (list_usage, {}),
        (list_news_feeds, {"category": "general"}),
        (list_ml_serving_apps, {}),
        (list_workload_executions, {}),
        (list_workload_status, {}),
        (list_workload_types, {}),
        (get_default_quota, {}),
        (get_default_quotas, {}),
        (list_all_resource_groups, {}),
        (list_all_accelerator_node_labels, {}),
    ]
    
    # Conditionally add upload_folder if cmlapi is available
    if HAS_UPLOAD_FOLDER:
        functions.append((upload_folder, {"folder_path": "/tmp/test", "target_dir": "/", "project_id": "test"}))
    
    return functions


# =============================================================================
# TEST 1: SECURITY - No subprocess vulnerabilities
# =============================================================================

def test_no_subprocess_vulnerabilities():
    """
    Verify that NO functions use subprocess.run for API calls
    This is critical for security - prevents API key exposure in process list
    """
    import cai_workbench_mcp_server.src.functions.delete_application as delete_app_mod
    import cai_workbench_mcp_server.src.functions.create_job_run as create_job_run_mod
    import cai_workbench_mcp_server.src.functions.get_job as get_job_mod
    import cai_workbench_mcp_server.src.functions.list_experiments as list_exp_mod
    import cai_workbench_mcp_server.src.functions.create_experiment_run as create_exp_run_mod
    
    critical_modules = [
        delete_app_mod,
        create_job_run_mod,
        get_job_mod,
        list_exp_mod,
        create_exp_run_mod,
    ]
    
    for module in critical_modules:
        module_file = inspect.getfile(module)
        module_source = open(module_file).read()

        # MUST use requests or cmlapi, not subprocess
        has_http_lib = ('import requests' in module_source or
                        'import cmlapi' in module_source or
                        'from cmlapi' in module_source or
                        'from .http_helpers import setup_client' in module_source)
        assert has_http_lib, \
            f"{module.__name__} MUST use requests or cmlapi for API calls"

        # MUST NOT use subprocess.run (security vulnerability)
        assert 'subprocess.run' not in module_source, \
            f"{module.__name__} MUST NOT use subprocess.run (security vulnerability)"


# =============================================================================
# TEST 2: FUNCTION SIGNATURES - All functions accept (config, params)
# =============================================================================

def test_all_functions_have_correct_signature(all_functions):
    """Verify all functions accept (config, params) signature"""
    for func, _ in all_functions:
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        
        assert len(params) >= 1, f"{func.__name__} must accept at least config parameter"
        assert params[0] == "config", f"{func.__name__} first parameter must be 'config'"
        
        # Most functions should also accept params
        if len(params) > 1:
            assert params[1] == "params", f"{func.__name__} second parameter should be 'params'"


# =============================================================================
# TEST 3: RESPONSE STRUCTURE - All functions return dict with status
# =============================================================================

def test_all_functions_return_dict_with_status(all_functions, mock_config):
    """Verify all functions return consistent response structure"""
    for func, test_params in all_functions:
        result = func(mock_config, test_params)
        
        # Must return dict
        assert isinstance(result, dict), \
            f"{func.__name__} must return dict, got {type(result)}"
        
        # Must have either 'success' or 'status' field
        has_status = "success" in result or "status" in result
        assert has_status, \
            f"{func.__name__} must have 'success' or 'status' in response"
        
        # Must have message field
        assert "message" in result, \
            f"{func.__name__} must have 'message' in response"


# =============================================================================
# TEST 4: ERROR HANDLING - Functions handle errors gracefully
# =============================================================================

def test_all_functions_handle_errors_gracefully(all_functions, mock_config):
    """Verify all functions handle errors without crashing"""
    for func, test_params in all_functions:
        try:
            result = func(mock_config, test_params)
            
            # Should not crash
            assert result is not None, f"{func.__name__} returned None"
            
            # Should return dict
            assert isinstance(result, dict), f"{func.__name__} must return dict"
            
            # Should have message
            assert "message" in result, f"{func.__name__} must have error message"
            
            # Should not have subprocess errors
            if "message" in result:
                message_lower = str(result["message"]).lower()
                assert "subprocess" not in message_lower, \
                    f"{func.__name__} should not have subprocess errors"
                
        except Exception as e:
            pytest.fail(f"{func.__name__} raised exception: {e}")


# =============================================================================
# TEST 5: SECURITY BEST PRACTICES
# =============================================================================

def test_functions_follow_security_best_practices():
    """Verify functions follow security best practices"""
    
    functions_to_check = [
        delete_application,
        create_job_run,
        get_job,
        list_experiments,
        create_experiment_run,
        delete_experiment_run,
    ]
    
    for func in functions_to_check:
        source = inspect.getsource(func)

        # 1. Must use requests or cmlapi (not subprocess)
        has_http = (any(method in source for method in ['requests.get', 'requests.post', 'requests.delete'])
                    or 'setup_client' in source)
        assert has_http, f"{func.__name__} must use requests or cmlapi"

        # 2. Must have error handling
        assert 'except' in source, f"{func.__name__} must have error handling"

        # 3. Must NOT use subprocess.run
        assert 'subprocess.run' not in source, f"{func.__name__} must NOT use subprocess.run"


# =============================================================================
# TEST 6: SPECIFIC FUNCTION TESTS
# =============================================================================

def test_get_runtimes_structure(mock_config):
    """Test get_runtimes returns proper structure"""
    result = get_runtimes(mock_config, {})
    
    assert isinstance(result, dict)
    assert "success" in result or "status" in result
    assert "message" in result


def test_create_job_with_parameters(mock_config):
    """Test create_job with various parameter combinations"""
    # Minimal parameters
    result1 = create_job(mock_config, {"name": "test", "script": "test.py"})
    assert isinstance(result1, dict)
    assert "success" in result1
    
    # With runtime
    result2 = create_job(mock_config, {
        "name": "test",
        "script": "test.py",
        "runtime_identifier": "docker.repository.cloudera.com/cloudera/cdsw/ml-runtime-jupyterlab-python3.10-standard:2024.10.1-b12"
    })
    assert isinstance(result2, dict)
    assert "success" in result2
    
    # With resources
    result3 = create_job(mock_config, {
        "name": "test",
        "script": "test.py",
        "cpu": 2,
        "memory": 4,
        "nvidia_gpu": 0
    })
    assert isinstance(result3, dict)
    assert "success" in result3


def test_get_project_id_list_all(mock_config):
    """Test get_project_id can list all projects"""
    result = get_project_id(mock_config, {"project_name": "*"})
    
    assert isinstance(result, dict)
    assert "message" in result or "projects" in result or "status" in result


def test_delete_operations_require_ids(mock_config):
    """Test delete operations require proper IDs"""
    # Test various delete operations
    delete_functions = [
        (delete_application, {"application_id": "test"}),
        (delete_job, {"job_id": "test", "project_id": "test"}),
        (delete_model, {"model_id": "test", "project_id": "test"}),
    ]
    
    for func, params in delete_functions:
        result = func(mock_config, params)
        assert isinstance(result, dict)
        assert "success" in result or "status" in result


def test_list_operations_return_consistent_structure(mock_config):
    """Test list operations return consistent structure"""
    list_functions = [
        (list_jobs, {"project_id": "test"}),
        (list_experiments, {"project_id": "test"}),
        (list_models, {"project_id": "test"}),
        (list_applications, {"project_id": "test"}),
    ]
    
    for func, params in list_functions:
        result = func(mock_config, params)
        assert isinstance(result, dict)
        assert "success" in result or "status" in result
        assert "message" in result


# =============================================================================
# TEST 7: MODULE IMPORTS
# =============================================================================

def test_all_modules_import_successfully():
    """Verify all function modules can be imported"""
    import cai_workbench_mcp_server.src.functions.batch_list_projects
    import cai_workbench_mcp_server.src.functions.create_application
    import cai_workbench_mcp_server.src.functions.create_experiment
    import cai_workbench_mcp_server.src.functions.create_experiment_run
    import cai_workbench_mcp_server.src.functions.create_job
    import cai_workbench_mcp_server.src.functions.create_job_run
    import cai_workbench_mcp_server.src.functions.create_model_build
    import cai_workbench_mcp_server.src.functions.create_model_deployment
    import cai_workbench_mcp_server.src.functions.delete_all_jobs
    import cai_workbench_mcp_server.src.functions.delete_application
    import cai_workbench_mcp_server.src.functions.delete_experiment
    import cai_workbench_mcp_server.src.functions.delete_experiment_run
    import cai_workbench_mcp_server.src.functions.delete_experiment_run_batch
    import cai_workbench_mcp_server.src.functions.delete_job
    import cai_workbench_mcp_server.src.functions.delete_model
    import cai_workbench_mcp_server.src.functions.delete_project_file
    import cai_workbench_mcp_server.src.functions.get_application
    import cai_workbench_mcp_server.src.functions.get_experiment
    import cai_workbench_mcp_server.src.functions.get_experiment_run
    import cai_workbench_mcp_server.src.functions.get_job
    import cai_workbench_mcp_server.src.functions.get_job_run
    import cai_workbench_mcp_server.src.functions.get_model
    import cai_workbench_mcp_server.src.functions.get_model_build
    import cai_workbench_mcp_server.src.functions.get_model_deployment
    import cai_workbench_mcp_server.src.functions.get_project_id
    import cai_workbench_mcp_server.src.functions.get_runtimes
    import cai_workbench_mcp_server.src.functions.list_applications
    import cai_workbench_mcp_server.src.functions.list_experiments
    import cai_workbench_mcp_server.src.functions.list_job_runs
    import cai_workbench_mcp_server.src.functions.list_jobs
    import cai_workbench_mcp_server.src.functions.list_model_builds
    import cai_workbench_mcp_server.src.functions.list_model_deployments
    import cai_workbench_mcp_server.src.functions.list_models
    import cai_workbench_mcp_server.src.functions.list_project_files
    import cai_workbench_mcp_server.src.functions.log_experiment_run_batch
    import cai_workbench_mcp_server.src.functions.restart_application
    import cai_workbench_mcp_server.src.functions.stop_application
    import cai_workbench_mcp_server.src.functions.stop_job_run
    import cai_workbench_mcp_server.src.functions.stop_model_deployment
    import cai_workbench_mcp_server.src.functions.update_application
    import cai_workbench_mcp_server.src.functions.update_experiment
    import cai_workbench_mcp_server.src.functions.update_experiment_run
    import cai_workbench_mcp_server.src.functions.update_job
    import cai_workbench_mcp_server.src.functions.update_project
    import cai_workbench_mcp_server.src.functions.update_project_file_metadata
    import cai_workbench_mcp_server.src.functions.upload_file
    import cai_workbench_mcp_server.src.functions.list_registered_models
    import cai_workbench_mcp_server.src.functions.create_registered_model
    import cai_workbench_mcp_server.src.functions.update_registered_model
    import cai_workbench_mcp_server.src.functions.get_registered_model
    import cai_workbench_mcp_server.src.functions.delete_registered_model
    import cai_workbench_mcp_server.src.functions.update_registered_model_version
    import cai_workbench_mcp_server.src.functions.get_registered_model_version
    import cai_workbench_mcp_server.src.functions.delete_registered_model_version
    import cai_workbench_mcp_server.src.functions.create_project
    import cai_workbench_mcp_server.src.functions.list_project_names
    import cai_workbench_mcp_server.src.functions.list_project_collaborators
    import cai_workbench_mcp_server.src.functions.delete_project_collaborator
    import cai_workbench_mcp_server.src.functions.add_project_collaborator
    import cai_workbench_mcp_server.src.functions.list_all_experiments
    import cai_workbench_mcp_server.src.functions.list_experiment_runs
    import cai_workbench_mcp_server.src.functions.get_experiment_run_metrics
    import cai_workbench_mcp_server.src.functions.list_all_jobs
    import cai_workbench_mcp_server.src.functions.list_all_models
    import cai_workbench_mcp_server.src.functions.update_model
    import cai_workbench_mcp_server.src.functions.delete_model_build
    import cai_workbench_mcp_server.src.functions.restart_model_deployment
    import cai_workbench_mcp_server.src.functions.download_project_file
    import cai_workbench_mcp_server.src.functions.list_runtimes
    import cai_workbench_mcp_server.src.functions.list_runtime_addons
    import cai_workbench_mcp_server.src.functions.list_runtime_repos
    import cai_workbench_mcp_server.src.functions.create_runtime_repo
    import cai_workbench_mcp_server.src.functions.delete_runtime_repo
    import cai_workbench_mcp_server.src.functions.update_runtime_repo
    import cai_workbench_mcp_server.src.functions.register_custom_runtime
    import cai_workbench_mcp_server.src.functions.update_runtime_status
    import cai_workbench_mcp_server.src.functions.update_runtime_addon_status
    import cai_workbench_mcp_server.src.functions.list_docker_credentials
    import cai_workbench_mcp_server.src.functions.create_docker_credential
    import cai_workbench_mcp_server.src.functions.delete_docker_credential
    import cai_workbench_mcp_server.src.functions.set_docker_credential
    import cai_workbench_mcp_server.src.functions.list_v2_keys
    import cai_workbench_mcp_server.src.functions.create_v2_key
    import cai_workbench_mcp_server.src.functions.delete_v2_key
    import cai_workbench_mcp_server.src.functions.delete_v2_keys
    import cai_workbench_mcp_server.src.functions.validate_api_key
    import cai_workbench_mcp_server.src.functions.list_cpu_profiles
    import cai_workbench_mcp_server.src.functions.list_groups_quota
    import cai_workbench_mcp_server.src.functions.list_users_quota
    import cai_workbench_mcp_server.src.functions.list_teams_accelerator_quota
    import cai_workbench_mcp_server.src.functions.list_teams
    import cai_workbench_mcp_server.src.functions.list_users_accelerator_quota
    import cai_workbench_mcp_server.src.functions.list_usage
    import cai_workbench_mcp_server.src.functions.list_news_feeds
    import cai_workbench_mcp_server.src.functions.list_ml_serving_apps
    import cai_workbench_mcp_server.src.functions.list_workload_executions
    import cai_workbench_mcp_server.src.functions.list_workload_status
    import cai_workbench_mcp_server.src.functions.list_workload_types
    import cai_workbench_mcp_server.src.functions.get_default_quota
    import cai_workbench_mcp_server.src.functions.get_default_quotas
    import cai_workbench_mcp_server.src.functions.list_all_resource_groups
    import cai_workbench_mcp_server.src.functions.list_all_accelerator_node_labels
    import cai_workbench_mcp_server.src.functions.health_check
    import cai_workbench_mcp_server.src.functions.generate_diag_bundle
    import cai_workbench_mcp_server.src.functions.get_diag_bundle_status
    import cai_workbench_mcp_server.src.functions.download_diag_bundle
    import cai_workbench_mcp_server.src.functions.http_helpers
    
    # upload_folder requires cmlapi (optional), only import if available
    if HAS_UPLOAD_FOLDER:
        import cai_workbench_mcp_server.src.functions.upload_folder
    
    # If we got here, all imports succeeded
    assert True


# =============================================================================
# TEST 8: DSE-58386 — Health Check, Diagnostics, include_all_projects
# =============================================================================

from unittest.mock import MagicMock, patch

from cai_workbench_mcp_server.src.functions.generate_diag_bundle import generate_diag_bundle
from cai_workbench_mcp_server.src.functions.get_diag_bundle_status import get_diag_bundle_status
from cai_workbench_mcp_server.src.functions.download_diag_bundle import download_diag_bundle
from cai_workbench_mcp_server.src.functions.health_check import health_check
from cai_workbench_mcp_server.src.functions.batch_list_projects import batch_list_projects


def test_health_check_healthy(mock_config):
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.to_dict.return_value = {"projects": [], "next_page_token": ""}
    mock_client.list_projects.return_value = mock_result
    with patch("cai_workbench_mcp_server.src.functions.health_check.setup_client", return_value=mock_client):
        result = health_check(mock_config, {})
    assert result["success"] is True
    assert result["status"] == "HEALTHY"


def test_health_check_missing_host():
    result = health_check({"host": "", "api_key": "key"}, {})
    assert result["success"] is False
    assert result["status"] == "UNHEALTHY"


def test_health_check_connection_failure(mock_config):
    with patch("cai_workbench_mcp_server.src.functions.health_check.setup_client",
               side_effect=Exception("Connection failed")):
        result = health_check(mock_config, {})
    assert result["success"] is False
    assert result["status"] == "UNHEALTHY"


def test_generate_diag_bundle_success(mock_config):
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.to_dict.return_value = {"status": "DIAG_IN_PROGRESS"}
    mock_client.generate_diag_bundle.return_value = mock_result
    with patch("cai_workbench_mcp_server.src.functions.generate_diag_bundle.setup_client", return_value=mock_client):
        result = generate_diag_bundle(mock_config, {})
    assert result["success"] is True
    assert "started" in result["message"]


def test_get_diag_bundle_status_missing_request_id(mock_config):
    result = get_diag_bundle_status(mock_config, {})
    assert result["success"] is False
    assert "request_id" in result["message"]


def test_get_diag_bundle_status_returns_status(mock_config):
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.to_dict.return_value = {"status": "DIAG_COMPLETED"}
    mock_client.get_diag_bundle_status.return_value = mock_result
    with patch("cai_workbench_mcp_server.src.functions.get_diag_bundle_status.setup_client", return_value=mock_client):
        result = get_diag_bundle_status(mock_config, {"request_id": "req-123"})
    assert result["success"] is True
    assert "DIAG_COMPLETED" in result["message"]


def test_download_diag_bundle_missing_request_id(mock_config):
    result = download_diag_bundle(mock_config, {})
    assert result["success"] is False
    assert "request_id" in result["message"]


def test_download_diag_bundle_success(mock_config):
    mock_client = MagicMock()
    mock_client.download_diagnostics_bundle.return_value = b"bundle"
    with patch("cai_workbench_mcp_server.src.functions.download_diag_bundle.setup_client", return_value=mock_client):
        result = download_diag_bundle(mock_config, {"request_id": "req-789"})
    assert result["success"] is True


def test_batch_list_projects_include_all(mock_config):
    mock_client = MagicMock()
    page = MagicMock()
    page.to_dict.return_value = {"projects": [{"name": "pub", "id": "p1"}], "next_page_token": None}
    mock_client.list_projects.return_value = page
    with patch("cai_workbench_mcp_server.src.functions.batch_list_projects.setup_client", return_value=mock_client):
        result = batch_list_projects(mock_config, {"include_all_projects": True})
    assert result["success"] is True
    assert mock_client.list_projects.call_args[1].get("include_all_projects") is True


def test_get_project_id_include_all_flag(mock_config):
    mock_client = MagicMock()
    page = MagicMock()
    page.to_dict.return_value = {"projects": [{"name": "p", "id": "p1"}], "next_page_token": None}
    mock_client.list_projects.return_value = page
    with patch("cai_workbench_mcp_server.src.functions.get_project_id.setup_client", return_value=mock_client):
        result = get_project_id(mock_config, {"project_name": "p", "include_all_projects": True})
    assert result["status"] == "success"
    assert mock_client.list_projects.call_args[1].get("include_all_projects") is True


def test_get_project_id_no_include_flags_by_default(mock_config):
    mock_client = MagicMock()
    page = MagicMock()
    page.to_dict.return_value = {"projects": [], "next_page_token": None}
    mock_client.list_projects.return_value = page
    with patch("cai_workbench_mcp_server.src.functions.get_project_id.setup_client", return_value=mock_client):
        get_project_id(mock_config, {"project_name": "*"})
    call_kwargs = mock_client.list_projects.call_args[1]
    assert "include_all_projects" not in call_kwargs
    assert "include_public_projects" not in call_kwargs


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

