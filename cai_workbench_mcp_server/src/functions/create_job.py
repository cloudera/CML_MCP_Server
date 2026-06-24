"""Create a job in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def create_job(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new job in a Cloudera AI project."""
    params = params or {}
    project_id = params.get("project_id") or config.get("project_id")

    if not project_id:
        return {"success": False, "message": "project_id is required"}
    if not params.get("name"):
        return {"success": False, "message": "name is required"}
    if not params.get("script"):
        return {"success": False, "message": "script is required"}

    body = {
        "name": params["name"],
        "script": params["script"],
        "kernel": params.get("kernel", "python3"),
        "cpu": params.get("cpu", 1),
        "memory": params.get("memory", 1),
        "nvidia_gpu": params.get("nvidia_gpu", 0),
    }
    if params.get("runtime_identifier"):
        body["runtime_identifier"] = params["runtime_identifier"]
    if params.get("environment_variables"):
        import json as _json
        env = params["environment_variables"]
        body["environment"] = _json.loads(env) if isinstance(env, str) else env

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.create_job(body, project_id)
        return {
            "success": True,
            "message": f"Successfully created job",
            "data": serialize_result(result),
        }
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error creating job: {str(e)}"}
