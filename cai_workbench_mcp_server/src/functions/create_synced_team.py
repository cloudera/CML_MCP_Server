"""Create a synced (LDAP/CDP group-backed) team in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def create_synced_team(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new synced team backed by one or more CDP/LDAP groups."""
    params = params or {}
    if not params.get("username"):
        return {"success": False, "message": "username is required"}
    if not params.get("group_permissions"):
        return {"success": False, "message": "group_permissions (list of {cn, permission}) is required"}

    body = {
        "username": params["username"],
        "group_permissions": params["group_permissions"],
    }
    if params.get("bio"):
        body["bio"] = params["bio"]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.create_synced_team(body)
        return {"success": True, "message": f"Synced team '{params['username']}' created", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
