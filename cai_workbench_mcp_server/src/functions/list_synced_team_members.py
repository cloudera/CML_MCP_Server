"""List members of a synced team with CDP group info in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def list_synced_team_members(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """List all members of a synced team along with their CDP group membership info."""
    params = params or {}
    if not params.get("team_name"):
        return {"success": False, "message": "team_name is required"}

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.list_synced_team_members(params["team_name"])
        return {"success": True, "message": "list_synced_team_members ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
