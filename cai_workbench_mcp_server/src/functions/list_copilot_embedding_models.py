"""List Copilot embedding models in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def list_copilot_embedding_models(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """List all Copilot embedding models, optionally filtered, sorted, and paginated."""
    params = params or {}
    kwargs = {}
    for key in ("search_filter", "sort", "page_size", "page_token"):
        if params.get(key) is not None:
            kwargs[key] = params[key]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.list_copilot_embedding_models(**kwargs)
        return {"success": True, "message": "list_copilot_embedding_models ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
