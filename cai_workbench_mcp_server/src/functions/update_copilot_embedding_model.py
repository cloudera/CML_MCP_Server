"""Update a Copilot embedding model in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def update_copilot_embedding_model(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Update fields of an existing Copilot embedding model."""
    params = params or {}
    if not params.get("id"):
        return {"success": False, "message": "id is required"}

    body = {"id": params["id"]}
    for key in ("provider", "name", "endpoint", "enabled", "default", "provider_id"):
        if params.get(key) is not None:
            body[key] = params[key]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.update_copilot_embedding_model({"copilot_embedding_model": body}, params["id"])
        return {"success": True, "message": f"Copilot embedding model '{params['id']}' updated", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
