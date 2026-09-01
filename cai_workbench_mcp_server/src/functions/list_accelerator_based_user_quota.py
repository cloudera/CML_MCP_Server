"""List accelerator-based user quotas in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def list_accelerator_based_user_quota(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """List per-user GPU quota allocations for each accelerator node label."""
    params = params or {}
    kwargs = {}
    for key in ("search_filter", "sort", "page_size", "page_token", "display_all"):
        if params.get(key) is not None:
            kwargs[key] = params[key]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.list_accelerator_based_user_quota(**kwargs)
        return {"success": True, "message": "list_accelerator_based_user_quota ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
