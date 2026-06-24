"""Batch list all projects in Cloudera AI."""

from typing import Any, Dict
try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None
from .http_helpers import setup_client, serialize_result

def batch_list_projects(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """List all projects with pagination.

    Args:
        config: MCP configuration with host and api_key
        params: Optional parameters:
            - include_all_projects: If true, returns all workspace projects (admin) or all accessible projects including public ones
            - include_public_projects: If true, includes public projects the user can access
            - search_filter: Filter string e.g. {"name":"foo"}
    """
    params = params or {}
    try:
        client = setup_client(config["host"], config["api_key"])
        all_projects = []
        page_token = None
        base_kwargs = {"page_size": 100}
        if params.get("include_all_projects"):
            base_kwargs["include_all_projects"] = True
        elif params.get("include_public_projects"):
            base_kwargs["include_public_projects"] = True
        if params.get("search_filter"):
            base_kwargs["search_filter"] = params["search_filter"]
        while True:
            kwargs = dict(base_kwargs)
            if page_token:
                kwargs["page_token"] = page_token
            result = client.list_projects(**kwargs)
            data = result.to_dict() if hasattr(result, "to_dict") else result
            projects = data.get("projects", [])
            all_projects.extend(projects)
            page_token = data.get("next_page_token")
            if not page_token:
                break
        return {"success": True, "message": f"Found {len(all_projects)} projects", "data": {"projects": all_projects, "count": len(all_projects)}}
    except ApiException as e:
        return {"success": False, "message": f"API error: {e.status} - {e.body}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
