"""Get the latest team sync status in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def teams_sync_status(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch the latest team synchronisation status from the identity provider."""
    params = params or {}
    kwargs = {}
    if params.get("request_id"):
        kwargs["request_id"] = params["request_id"]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.teams_sync_status(**kwargs)
        return {"success": True, "message": "teams_sync_status ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
