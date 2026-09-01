"""Update accelerator-based team quotas in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def update_accelerator_based_team_quota(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Update GPU quota allocations for one or more teams on accelerator node labels."""
    params = params or {}
    if not params.get("accelerator_based_team_quota"):
        return {"success": False, "message": "accelerator_based_team_quota (list of {team_id, accelerator_id, gpu_quota}) is required"}

    body = {"accelerator_based_team_quota": params["accelerator_based_team_quota"]}
    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.update_accelerator_based_team_quota(body)
        return {"success": True, "message": "Team accelerator quotas updated", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
