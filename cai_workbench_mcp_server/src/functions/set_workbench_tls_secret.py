"""Set the TLS secret used by CML Workbenches."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def set_workbench_tls_secret(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Create or update the TLS certificate secret used by CML Workbenches."""
    params = params or {}
    if not params.get("tls_crt"):
        return {"success": False, "message": "tls_crt (base64-encoded PEM cert) is required"}
    if not params.get("tls_key"):
        return {"success": False, "message": "tls_key (base64-encoded PEM key) is required"}

    body = {"tls_crt": params["tls_crt"], "tls_key": params["tls_key"]}
    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.set_workbench_tls_secret(body)
        return {"success": True, "message": "set_workbench_tls_secret ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
