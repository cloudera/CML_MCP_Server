"""Delete a team in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def delete_team(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Delete a team from the workspace."""
    params = params or {}
    if not params.get("team_name"):
        return {"success": False, "message": "team_name is required"}

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.delete_team(params["team_name"])
        return {"success": True, "message": f"Team '{params['team_name']}' deleted", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
