"""Validate a custom runtime image in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def validate_custom_runtime(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a custom runtime image URL before registering it."""
    params = params or {}
    if not params.get("url"):
        return {"success": False, "message": "url is required"}

    kwargs = {"url": params["url"]}
    if params.get("docker_credential_id"):
        kwargs["docker_credential_id"] = params["docker_credential_id"]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.validate_custom_runtime(**kwargs)
        return {"success": True, "message": "validate_custom_runtime ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
