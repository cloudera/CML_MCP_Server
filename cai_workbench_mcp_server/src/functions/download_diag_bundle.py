"""Download a diagnostics bundle from Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client


def download_diag_bundle(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Download a completed diagnostics bundle.

    The bundle must have status DIAG_COMPLETED before downloading.
    Use get_diag_bundle_status to check progress first.

    Args:
        config: MCP configuration with host and api_key
        params:
            - request_id: The request ID of the completed bundle (required)

    Returns:
        Dict with success flag, message, and download info
    """
    params = params or {}
    request_id = params.get("request_id")
    if not request_id:
        return {"success": False, "message": "request_id is required"}

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.download_diagnostics_bundle(request_id)
        # Returns binary content or a file path depending on SDK config
        return {
            "success": True,
            "message": f"Diagnostics bundle downloaded for request '{request_id}'",
            "data": {"request_id": request_id, "content": str(result) if result else "downloaded"},
        }
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error downloading diagnostics bundle: {str(e)}"}
