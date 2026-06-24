"""Health check for Cloudera AI Workbench connectivity."""

from typing import Any, Dict

try:
    from cmlapi.rest import ApiException
except ImportError:
    class ApiException(Exception):
        """Placeholder when cmlapi is not installed."""
        status = None
        body = None

from .http_helpers import setup_client


def health_check(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Check connectivity and authentication to Cloudera AI Workbench.

    Validates that the host is reachable and the API key is valid by
    making a lightweight list_projects call.

    Args:
        config: MCP configuration with host and api_key

    Returns:
        Dict with success flag, status, and connection details
    """
    params = params or {}
    host = config.get("host", "")
    if not host:
        return {"success": False, "status": "UNHEALTHY", "message": "No host configured"}

    try:
        client = setup_client(host, config.get("api_key", ""))
        result = client.list_projects(page_size=1)
        data = result.to_dict() if hasattr(result, "to_dict") else result
        total = data.get("next_page_token")  # presence means more pages = connected
        return {
            "success": True,
            "status": "HEALTHY",
            "message": f"Connected to {host}",
            "data": {"host": host, "authenticated": True},
        }
    except ApiException as e:
        status = "UNHEALTHY"
        if e.status == 401:
            message = "Authentication failed — check your API key"
        elif e.status == 403:
            message = "Authorisation denied — insufficient permissions"
        else:
            message = f"API error: {e.status} - {e.body}"
        return {"success": False, "status": status, "message": message}
    except Exception as e:
        return {
            "success": False,
            "status": "UNHEALTHY",
            "message": f"Connection failed: {str(e)}",
            "data": {"host": host},
        }
