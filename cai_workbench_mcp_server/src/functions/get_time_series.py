"""Get time series resource data in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def get_time_series(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch time series data for CPU, memory, or GPU usage across workloads."""
    params = params or {}
    kwargs = {}
    for key in ("search_filter", "page_token", "multi_column_search_filter", "time_range_search_filter", "series_type"):
        if params.get(key) is not None:
            kwargs[key] = params[key]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.get_time_series(**kwargs)
        return {"success": True, "message": "get_time_series ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
