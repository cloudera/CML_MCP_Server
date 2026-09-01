"""Update admin config (max GPU per workload) for accelerator node labels in Cloudera AI."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client, serialize_result


def update_accelerator_labels_admin_config(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Update the admin_config_max_per_workload for multiple accelerator node labels at once."""
    params = params or {}
    if not params.get("id_max_gpu_workload"):
        return {"success": False, "message": "id_max_gpu_workload (dict of {label_id: max_gpu}) is required"}

    body = {"id_max_gpu_workload": params["id_max_gpu_workload"]}
    try:
        client = setup_client(config["host"], config["api_key"])
        result = client.update_accelerator_labels_admin_config(body)
        return {"success": True, "message": "Admin config updated", "data": serialize_result(result)}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
