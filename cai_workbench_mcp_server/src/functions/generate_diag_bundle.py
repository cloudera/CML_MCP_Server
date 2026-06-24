"""Generate a diagnostics bundle in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def generate_diag_bundle(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a diagnostics bundle.

    Args:
        config: MCP configuration with host and api_key
        params: Optional parameters:
            - start_time: Start time for the bundle (optional)
            - end_time: End time for the bundle (optional)

    Returns:
        Dict with success flag, message, and request_id to track status
    """
    params = params or {}

    body = {}
    if params.get("start_time"):
        body["start_time"] = params["start_time"]
    if params.get("end_time"):
        body["end_time"] = params["end_time"]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.generate_diag_bundle(body)
        data = serialize_result(result)
        return {
            "success": True,
            "message": "Diagnostics bundle generation started",
            "data": data,
        }
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error generating diagnostics bundle: {str(e)}"}
