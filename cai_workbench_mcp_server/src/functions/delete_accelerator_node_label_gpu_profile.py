"""Delete a GPU profile for an accelerator node label in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def delete_accelerator_node_label_gpu_profile(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Delete a GPU profile from an accelerator node label by resource group and profile ID."""
    params = params or {}
    if not params.get("resource_group_id"):
        return {"success": False, "message": "resource_group_id is required"}
    if not params.get("id"):
        return {"success": False, "message": "id is required"}

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.delete_accelerator_node_label_gpu_profile(params["resource_group_id"], params["id"])
        return {"success": True, "message": "GPU profile deleted", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
