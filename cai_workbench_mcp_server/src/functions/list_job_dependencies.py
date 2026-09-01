"""List job dependencies in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def list_job_dependencies(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """List all jobs in the dependency tree of a given job."""
    params = params or {}
    project_id = params.get("project_id") or config.get("project_id")
    job_id = params.get("job_id")

    if not project_id:
        return {"success": False, "message": "project_id is required"}
    if not job_id:
        return {"success": False, "message": "job_id is required"}

    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.list_job_dependencies(project_id, job_id)
        return {"success": True, "message": "list_job_dependencies ok", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
