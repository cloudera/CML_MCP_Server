"""Get abbreviated user info by user ID in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def get_short_user_by_id(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch abbreviated user information (username, name, email) for a given user ID."""
    params = params or {}
    if not params.get("user_id"):
        return {"success": False, "message": "user_id is required"}

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.get_short_user_by_id(params["user_id"])
        return {"success": True, "message": "get_short_user_by_id ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
