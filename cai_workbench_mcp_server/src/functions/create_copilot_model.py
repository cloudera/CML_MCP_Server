"""Create a Copilot language model in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def create_copilot_model(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Register a new Copilot language model (e.g. Amazon Bedrock or CML Serving)."""
    params = params or {}
    if not params.get("provider"):
        return {"success": False, "message": "provider is required"}
    if not params.get("name"):
        return {"success": False, "message": "name is required"}

    body = {"provider": params["provider"], "name": params["name"]}
    for key in ("endpoint", "enabled", "default", "provider_id"):
        if params.get(key) is not None:
            body[key] = params[key]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.create_copilot_model(body)
        return {"success": True, "message": "Copilot model created", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
