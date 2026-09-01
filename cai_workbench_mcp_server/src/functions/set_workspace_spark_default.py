"""Set workspace Spark default configuration in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def set_workspace_spark_default(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Set the workspace-level Spark default configuration string."""
    params = params or {}
    if not params.get("workspace_spark_default"):
        return {"success": False, "message": "workspace_spark_default is required"}
    if params.get("is_pushdown") not in ("true", "false"):
        return {"success": False, "message": "is_pushdown must be 'true' or 'false'"}

    body = {
        "workspace_spark_default": params["workspace_spark_default"],
        "is_pushdown": params["is_pushdown"],
    }
    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.set_workspace_spark_default(body)
        return {"success": True, "message": "Workspace Spark default set", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
