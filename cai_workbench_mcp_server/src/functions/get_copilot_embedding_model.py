"""Get a Copilot embedding model in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def get_copilot_embedding_model(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch details of a specific Copilot embedding model by ID."""
    params = params or {}
    if not params.get("copilot_embedding_model_id"):
        return {"success": False, "message": "copilot_embedding_model_id is required"}

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.get_copilot_embedding_model(params["copilot_embedding_model_id"])
        return {"success": True, "message": "get_copilot_embedding_model ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
