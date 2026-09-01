"""Set the default resource quota for a user in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def set_default_quota(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Set the default CPU/memory/GPU quota for a specific user (by UUID)."""
    params = params or {}
    if not params.get("uuid"):
        return {"success": False, "message": "uuid is required"}
    if not params.get("quota"):
        return {"success": False, "message": "quota (dict with requests_memory, requests_cpu, requests_gpu) is required"}

    body = {
        "uuid": params["uuid"],
        "quota": params["quota"],
    }
    if params.get("sync_mig_to_umbra") is not None:
        body["sync_mig_to_umbra"] = params["sync_mig_to_umbra"]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.set_default_quota(body)
        return {"success": True, "message": "Default quota set", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
