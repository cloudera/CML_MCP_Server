"""Disable or enable legacy engines site-wide in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def disable_engines(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Enable or disable legacy engines across all projects in the workspace."""
    params = params or {}
    if params.get("disable_engines") is None:
        return {"success": False, "message": "disable_engines (bool) is required"}

    body = {"disable_engines": bool(params["disable_engines"])}
    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.disable_engines(body)
        return {"success": True, "message": "disable_engines ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
