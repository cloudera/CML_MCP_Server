"""Delete a CPU resource profile in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def delete_cpu_profile(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Delete a CPU resource profile by ID."""
    params = params or {}
    if not params.get("id"):
        return {"success": False, "message": "id is required"}

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.delete_cpu_profile(params["id"])
        return {"success": True, "message": f"CPU profile '{params['id']}' deleted", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
