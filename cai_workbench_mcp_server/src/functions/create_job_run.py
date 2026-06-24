"""Create a job run in Cloudera AI."""

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


def create_job_run(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a run for an existing job."""
    params = params or {}
    project_id = params.get("project_id") or config.get("project_id")
    job_id = params.get("job_id")

    if not project_id:
        return {"success": False, "message": "project_id is required"}
    if not job_id:
        return {"success": False, "message": "job_id is required"}

    body = {}
    if params.get("runtime_identifier"):
        body["runtime_identifier"] = params["runtime_identifier"]
    if params.get("environment_variables"):
        env = params["environment_variables"]
        body["environment"] = json.loads(env) if isinstance(env, str) else env
    if params.get("override_config"):
        oc = params["override_config"]
        body["override_config"] = json.loads(oc) if isinstance(oc, str) else oc

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.create_job_run(body, project_id, job_id)
        return {
            "success": True,
            "message": f"Successfully created job run for job '{job_id}'",
            "data": serialize_result(result),
        }
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error creating job run: {str(e)}"}
