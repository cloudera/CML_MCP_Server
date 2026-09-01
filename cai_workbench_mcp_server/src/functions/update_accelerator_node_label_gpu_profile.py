"""Update a GPU profile for an accelerator node label in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def update_accelerator_node_label_gpu_profile(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Update CPU/memory for an existing GPU profile on an accelerator node label."""
    params = params or {}
    if not params.get("resource_group_id"):
        return {"success": False, "message": "resource_group_id is required"}
    if not params.get("id"):
        return {"success": False, "message": "id is required"}

    body = {
        "resource_group_id": params["resource_group_id"],
        "id": params["id"],
    }
    for key in ("gpu_count", "cpu", "memory"):
        if params.get(key) is not None:
            body[key] = params[key]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.update_accelerator_node_label_gpu_profile(body, params["resource_group_id"])
        return {"success": True, "message": "GPU profile updated", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
