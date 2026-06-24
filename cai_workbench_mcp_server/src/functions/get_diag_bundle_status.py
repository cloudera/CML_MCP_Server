"""Get diagnostics bundle status in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def get_diag_bundle_status(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Get the status of a diagnostics bundle generation request.

    Status values: DIAG_IN_PROGRESS, DIAG_COMPLETED, DIAG_FAILED, DIAG_NOT_STARTED

    Args:
        config: MCP configuration with host and api_key
        params:
            - request_id: The request ID returned by generate_diag_bundle (required)

    Returns:
        Dict with success flag, message, status, and data
    """
    params = params or {}
    request_id = params.get("request_id")
    if not request_id:
        return {"success": False, "message": "request_id is required"}

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.get_diag_bundle_status(request_id)
        data = serialize_result(result)
        status = data.get("status", "UNKNOWN")
        return {
            "success": True,
            "message": f"Diagnostics bundle status: {status}",
            "data": data,
        }
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error getting diagnostics bundle status: {str(e)}"}
