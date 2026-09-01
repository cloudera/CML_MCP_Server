"""Update default quota for accelerator node labels in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def update_accelerator_labels_default_quota(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Update the default_quota and/or default_team_quota for accelerator node labels."""
    params = params or {}
    body = {}
    if params.get("id_default_quota"):
        body["id_default_quota"] = params["id_default_quota"]
    if params.get("id_default_team_quota"):
        body["id_default_team_quota"] = params["id_default_team_quota"]
    if not body:
        return {"success": False, "message": "id_default_quota or id_default_team_quota is required"}

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.update_accelerator_labels_default_quota(body)
        return {"success": True, "message": "Default quota updated", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
