"""Create a GPU profile for an accelerator node label in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def create_accelerator_node_label_gpu_profile(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a GPU profile (cpu/memory allocation per GPU count) for a resource group."""
    params = params or {}
    if not params.get("resource_group_id"):
        return {"success": False, "message": "resource_group_id is required"}
    if not params.get("gpu_count"):
        return {"success": False, "message": "gpu_count is required"}

    body = {
        "resource_group_id": params["resource_group_id"],
        "gpu_count": params["gpu_count"],
    }
    for key in ("cpu", "memory"):
        if params.get(key) is not None:
            body[key] = params[key]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.create_accelerator_node_label_gpu_profile(body, params["resource_group_id"])
        return {"success": True, "message": "GPU profile created", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
