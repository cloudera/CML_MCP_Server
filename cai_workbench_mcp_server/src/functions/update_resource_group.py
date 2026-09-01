"""Update a resource group in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def update_resource_group(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Update workload allowances for an existing resource group."""
    params = params or {}
    if not params.get("id"):
        return {"success": False, "message": "id is required"}

    body = {"id": params["id"]}
    for key in ("allow_jobs", "allow_sessions", "allow_models", "allow_applications"):
        if params.get(key) is not None:
            body[key] = params[key]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.update_resource_group({"resource_group": body}, params["id"])
        return {"success": True, "message": f"Resource group '{params['id']}' updated", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
