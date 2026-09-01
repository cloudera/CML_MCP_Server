"""Validate a V2 API key in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def validate_api_key_v2(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a V2 API key and return the associated username and validity status."""
    params = params or {}
    if not params.get("audience"):
        return {"success": False, "message": "audience is required ('API' or 'Application')"}

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.validate_api_key(audience=params["audience"])
        return {"success": True, "message": "validate_api_key ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
