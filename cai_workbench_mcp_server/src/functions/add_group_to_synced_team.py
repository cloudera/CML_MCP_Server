"""Add a CDP group to a synced team in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def add_group_to_synced_team(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Add a CDP/LDAP group with a default permission to a synced team."""
    params = params or {}
    if not params.get("team_name"):
        return {"success": False, "message": "team_name is required"}
    if not params.get("cn"):
        return {"success": False, "message": "cn (group name) is required"}
    if not params.get("permission"):
        return {"success": False, "message": "permission is required (admin/operator/read/write)"}

    body = {"team_name": params["team_name"], "group_permission": {"cn": params["cn"], "permission": params["permission"]}}
    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.add_group_to_synced_team(body, params["team_name"])
        return {"success": True, "message": f"Group '{params['cn']}' added to team", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
