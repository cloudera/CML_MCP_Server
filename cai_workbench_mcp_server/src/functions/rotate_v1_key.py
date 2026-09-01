"""Rotate a user's V1 API key in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def rotate_v1_key(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Rotate the V1 API key for a given user."""
    params = params or {}
    if not params.get("username"):
        return {"success": False, "message": "username is required"}

    body = {"username": params["username"]}
    for key in ("api_key_expiry_date", "api_key_comments"):
        if params.get(key):
            body[key] = params[key]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.rotate_v1_key(body, params["username"])
        return {"success": True, "message": f"V1 key rotated for '{params['username']}'", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
