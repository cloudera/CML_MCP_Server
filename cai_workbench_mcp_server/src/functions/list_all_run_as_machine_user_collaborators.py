"""List all machine user (run-as) collaborators for a project in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def list_all_run_as_machine_user_collaborators(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """List all service account (machine user) collaborators available for run-as in a project."""
    params = params or {}
    project_id = params.get("project_id") or config.get("project_id")
    if not project_id:
        return {"success": False, "message": "project_id is required"}

    kwargs = {"project_id": project_id}
    for key in ("search_filter", "page_size", "page_token", "sort"):
        if params.get(key) is not None:
            kwargs[key] = params[key]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.list_all_run_as_machine_user_collaborators(**kwargs)
        return {"success": True, "message": "list_all_run_as_machine_user_collaborators ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
