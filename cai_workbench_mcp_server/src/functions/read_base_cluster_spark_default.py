"""Read base cluster Spark default configuration in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def read_base_cluster_spark_default(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Read the base cluster Spark default configuration values."""
    params = params or {}
    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.read_base_cluster_spark_default()
        return {"success": True, "message": "read_base_cluster_spark_default ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
