"""Update a Docker credential in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def update_docker_credential(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing Docker registry credential (name, server, username, password)."""
    params = params or {}
    if not params.get("id"):
        return {"success": False, "message": "id is required"}

    body = {"id": params["id"]}
    for key in ("name", "server", "username", "password", "is_default"):
        if params.get(key) is not None:
            body[key] = params[key]

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.update_docker_credential({"docker_credential": body}, params["id"])
        return {"success": True, "message": f"Docker credential '{params['id']}' updated", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
