"""Read workspace Spark default configuration in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def read_workspace_spark_default(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Read the current workspace-level Spark default configuration."""
    params = params or {}
    if params.get("is_pushdown") not in ("true", "false"):
        return {"success": False, "message": "is_pushdown must be 'true' or 'false'"}

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.read_workspace_spark_default(is_pushdown=params["is_pushdown"])
        return {"success": True, "message": "read_workspace_spark_default ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
