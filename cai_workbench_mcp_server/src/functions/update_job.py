"""Update a job in Cloudera AI."""

import json
from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def update_job(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing job."""
    params = params or {}
    project_id = params.get("project_id") or config.get("project_id")
    job_id = params.get("job_id")

    if not project_id:
        return {"success": False, "message": "project_id is required"}
    if not job_id:
        return {"success": False, "message": "job_id is required"}

    body = {}
    for key in ("name", "script", "kernel", "cpu", "memory", "nvidia_gpu", "runtime_identifier"):
        if params.get(key) is not None:
            body[key] = params[key]
    if params.get("environment_variables"):
        env = params["environment_variables"]
        body["environment"] = json.loads(env) if isinstance(env, str) else env

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.update_job(body, project_id, job_id)
        return {
            "success": True,
            "message": f"Successfully updated job '{job_id}'",
            "data": serialize_result(result),
        }
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error updating job: {str(e)}"}
