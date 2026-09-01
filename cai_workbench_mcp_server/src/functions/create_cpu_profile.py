"""Create a CPU resource profile in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def create_cpu_profile(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new CPU resource profile for a resource group."""
    params = params or {}
    if not params.get("resource_group_id"):
        return {"success": False, "message": "resource_group_id is required"}
    if not params.get("cpu"):
        return {"success": False, "message": "cpu is required"}
    if not params.get("memory"):
        return {"success": False, "message": "memory is required"}

    body = {
        "resource_group_id": params["resource_group_id"],
        "cpu": params["cpu"],
        "memory": params["memory"],
    }
    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.create_cpu_profile(body)
        return {"success": True, "message": "CPU profile created", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
