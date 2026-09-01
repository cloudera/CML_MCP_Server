"""Create a team in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def create_team(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new local team in the workspace."""
    params = params or {}
    if not params.get("username"):
        return {"success": False, "message": "username is required"}

    body = {"username": params["username"]}
    for key in ("type", "cn", "bio", "permission"):
        if params.get(key) is not None:
            body[key] = params[key]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.create_team(body)
        return {"success": True, "message": f"Team '{params['username']}' created", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
