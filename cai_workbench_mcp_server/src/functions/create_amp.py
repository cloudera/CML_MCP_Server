"""Create an AMP (Accelerators for ML Projects) in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def create_amp(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new AMP project from a git URL with optional runtime configuration."""
    params = params or {}
    if not params.get("name"):
        return {"success": False, "message": "name is required"}
    if not params.get("git_url"):
        return {"success": False, "message": "git_url is required"}

    create_project = {
        "name": params["name"],
        "git_url": params["git_url"],
        "template": "git",
        "default_project_engine_type": "ml_runtime",
    }
    for key in ("description", "visibility", "git_ref", "team_name"):
        if params.get(key):
            create_project[key] = params[key]

    configure_prototype = {
        "execute_amp_steps": params.get("execute_amp_steps", True),
        "run_import_tasks": params.get("run_import_tasks", True),
    }
    if params.get("runtime_identifier"):
        configure_prototype["runtime_identifier"] = params["runtime_identifier"]
    if params.get("runtime_addon_identifiers"):
        configure_prototype["runtime_addon_identifiers"] = params["runtime_addon_identifiers"]

    body = {
        "create_project_request": create_project,
        "configure_prototype_request": configure_prototype,
    }
    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.create_amp(body)
        return {"success": True, "message": "AMP project created", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
