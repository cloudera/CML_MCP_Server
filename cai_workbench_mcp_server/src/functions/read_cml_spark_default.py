"""Read CML Spark default configuration in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def read_cml_spark_default(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Read the CML-level Spark default for a given RAZ/pushdown context."""
    params = params or {}
    if params.get("raz_enabled") not in ("true", "false"):
        return {"success": False, "message": "raz_enabled must be 'true' or 'false'"}

    kwargs = {"raz_enabled": params["raz_enabled"]}
    if params.get("pushdown_enabled") in ("true", "false"):
        kwargs["pushdown_enabled"] = params["pushdown_enabled"]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.read_cml_spark_default(**kwargs)
        return {"success": True, "message": "read_cml_spark_default ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
