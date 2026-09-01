"""Update a team member's permission for a synced team in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def update_member_permission_for_synced_team(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Update the effective permission for a specific member within a synced team."""
    params = params or {}
    if not params.get("team_name"):
        return {"success": False, "message": "team_name is required"}
    if not params.get("user_id"):
        return {"success": False, "message": "user_id is required"}
    if not params.get("permission"):
        return {"success": False, "message": "permission is required (admin/inherit/operator/read/write)"}

    body = {"team_name": params["team_name"], "user_id": params["user_id"], "permission": params["permission"]}
    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.update_member_permission_for_synced_team(body, params["team_name"], params["user_id"])
        return {"success": True, "message": "Member permission updated", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
