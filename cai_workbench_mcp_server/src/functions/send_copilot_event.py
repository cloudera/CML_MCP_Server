"""Send a Copilot usage event in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def send_copilot_event(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Record a Copilot usage event (chat command, slash command, model selection, etc.)."""
    params = params or {}
    if not params.get("event_type"):
        return {"success": False, "message": "event_type is required"}

    body = {"event_type": params["event_type"]}
    for key in ("engine_id", "application_id", "event_details", "model_provider_id",
                "model_name", "model_type", "include_selection", "prompt_word_count"):
        if params.get(key) is not None:
            body[key] = params[key]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.send_copilot_event(body)
        return {"success": True, "message": "Copilot event sent", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
