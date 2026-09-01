"""Archive old engine dashboards in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def dashboards_archive(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Archive engine dashboards that have been finished for more than N days."""
    params = params or {}
    body = {}
    if params.get("days_finished") is not None:
        body["days_finished"] = int(params["days_finished"])

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.dashboards_archive(body)
        return {"success": True, "message": "dashboards_archive ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
