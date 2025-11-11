"""
Simple FastMCP-based Prometheus MCP server.

A clean, simple MCP server for basic Prometheus queries using FastMCP.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict

from fastmcp import FastMCP
import httpx

# Simple configuration from environment
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
PROMETHEUS_TIMEOUT = int(os.getenv("PROMETHEUS_TIMEOUT", "30"))
ALERTMANAGER_URL = os.getenv("ALERTMANAGER_URL", "http://localhost:9093")

# Create FastMCP app
mcp = FastMCP("Prometheus MCP Server")


class PrometheusClient:
    """Simple Prometheus client for basic queries."""

    def __init__(self, url: str, timeout: int = 30):
        self.url = url.rstrip('/')
        self.timeout = timeout

    async def query(self, promql: str) -> Dict[str, Any]:
        """Execute a simple PromQL query."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.url}/api/v1/query",
                params={"query": promql}
            )
            response.raise_for_status()
            return response.json()

    async def health_check(self) -> Dict[str, Any]:
        """Check Prometheus health."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.url}/-/healthy")
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": self.url
            }


class AlertmanagerClient:
    """Simple Alertmanager client for alert management."""

    def __init__(self, url: str, timeout: int = 30):
        self.url = url.rstrip('/')
        self.timeout = timeout

    async def get_alerts(self, active: bool = True) -> Dict[str, Any]:
        """Get alerts from Alertmanager."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {"active": "true"} if active else {}
            response = await client.get(f"{self.url}/api/v1/alerts", params=params)
            response.raise_for_status()
            return response.json()

    async def silence_alert(self, matchers: list, duration: str, created_by: str, comment: str) -> Dict[str, Any]:
        """Create an alert silence."""
        silence_data = {
            "matchers": matchers,
            "startsAt": datetime.utcnow().isoformat() + "Z",
            "endsAt": (datetime.utcnow() + timedelta(hours=int(duration.rstrip('h')))).isoformat() + "Z",
            "createdBy": created_by,
            "comment": comment
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.url}/api/v1/silences",
                json=silence_data
            )
            response.raise_for_status()
            return response.json()


# Global client instances
prometheus = PrometheusClient(PROMETHEUS_URL, PROMETHEUS_TIMEOUT)
alertmanager = AlertmanagerClient(ALERTMANAGER_URL, PROMETHEUS_TIMEOUT)

@mcp.resource("prometheus://alerts/firing")
async def get_firing_alerts() -> str:
    """Resource for currently firing alerts."""
    result = await prometheus.query('ALERTS{alertstate="firing"}')
    return json.dumps(result, indent=2)

@mcp.resource("prometheus://metrics/{metric_name}")
async def get_metric(metric_name: str) -> str:
    """Resource for specific metric data."""
    result = await prometheus.query(metric_name)
    return json.dumps(result, indent=2)

@mcp.resource("prometheus://dashboard/overview")
async def get_dashboard_overview() -> str:
    """Resource providing dashboard-like overview."""
    queries = {
        "cpu": "avg(100 - (avg by(instance) (irate(node_cpu_seconds_total{mode='idle'}[5m])) * 100))",
        "memory": "avg((1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100)",
        "disk": "avg(100 - ((node_filesystem_avail_bytes{fstype!='tmpfs'} / node_filesystem_size_bytes) * 100))",
        "alerts": "count(ALERTS{alertstate='firing'})"
    }
    
    overview = {}
    for name, query in queries.items():
        try:
            result = await prometheus.query(query)
            overview[name] = result
        except Exception as e:
            overview[name] = {"error": str(e)}
    
    return json.dumps(overview, indent=2)

@mcp.prompt()
async def analyze_alert_prompt(alert_name: str, timerange: str = "1h") -> str:
    """Generate analysis prompt for a specific alert."""
    alert_data = await prometheus.query(f'ALERTS{{alertname="{alert_name}"}}')
    
    return f"""
    Analyze this Prometheus alert:
    
    Alert: {alert_name}
    Time Range: {timerange}
    Data: {json.dumps(alert_data, indent=2)}
    
    Please provide:
    1. Root cause analysis
    2. Impact assessment
    3. Recommended actions
    4. Prevention strategies
    """

@mcp.prompt()
async def performance_analysis_prompt(service: str, duration: str = "24h") -> str:
    """Generate performance analysis prompt for a service."""
    queries = {
        "cpu": f'avg(rate(container_cpu_usage_seconds_total{{pod=~"{service}.*"}}[5m])) * 100',
        "memory": f'avg(container_memory_working_set_bytes{{pod=~"{service}.*"}}) / 1024 / 1024',
        "requests": f'sum(rate(http_requests_total{{service="{service}"}}[5m]))',
        "errors": f'sum(rate(http_requests_total{{service="{service}",status=~"5.."}}[5m]))'
    }
    
    metrics = {}
    for name, query in queries.items():
        try:
            result = await prometheus.query(query)
            metrics[name] = result
        except Exception as e:
            metrics[name] = {"error": str(e)}
    
    return f"""
    Performance Analysis for {service} (Last {duration}):
    
    Metrics: {json.dumps(metrics, indent=2)}
    
    Please analyze:
    1. Performance trends
    2. Bottlenecks identification
    3. Capacity planning recommendations
    4. Optimization opportunities
    """

@mcp.tool()
async def prometheus_query(query: str) -> str:
    """
    Execute a PromQL query against Prometheus.
    
    Args:
        query: PromQL query string (e.g., 'up', 'cpu_usage_percent')
    
    Returns:
        JSON formatted query results
    """
    try:
        result = await prometheus.query(query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error executing query: {e}"


@mcp.tool()
async def prometheus_health() -> str:
    """
    Check Prometheus server health status.
    
    Returns:
        Health status information
    """
    try:
        result = await prometheus.health_check()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error checking health: {e}"


@mcp.tool()
async def prometheus_cpu() -> str:
    """
    Get current CPU usage across all instances.
    
    Returns:
        CPU usage metrics
    """
    query = '100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    return await prometheus_query(query)


@mcp.tool()
async def prometheus_memory() -> str:
    """
    Get current memory usage across all instances.
    
    Returns:
        Memory usage metrics
    """
    query = '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100'
    return await prometheus_query(query)


@mcp.tool()
async def prometheus_services() -> str:
    """
    Check which services are up/down.
    
    Returns:
        Service status information
    """
    return await prometheus_query("up")


@mcp.tool()
async def alertmanager_get_alerts(active: bool = True) -> str:
    """
    Get alerts from Alertmanager.

    Args:
        active: If True, only return active alerts. If False, return all alerts.

    Returns:
        JSON formatted list of alerts from Alertmanager
    """
    try:
        result = await alertmanager.get_alerts(active=active)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting alerts from Alertmanager: {e}"


@mcp.tool()
async def alertmanager_silence(alert_name: str, duration: str, reason: str, created_by: str = "mcp-server") -> str:
    """
    Silence an alert in Alertmanager.

    Args:
        alert_name: Name of the alert to silence
        duration: Duration like '2h', '30m'
        reason: Reason for silencing
        created_by: Who is creating the silence
    """
    try:
        matchers = [{"name": "alertname", "value": alert_name, "isRegex": False}]
        result = await alertmanager.silence_alert(matchers, duration, created_by, reason)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating silence: {e}"

def run_server():
    """Run the MCP server."""
    print(f"Starting Prometheus MCP Server (connecting to {PROMETHEUS_URL})")
    mcp.run()


def main():
    """Handle command line and start server."""
    import sys
    
    # Simple help
    if len(sys.argv) > 1 and ("--help" in sys.argv or "-h" in sys.argv):
        print("Prometheus MCP Server")
        print("Usage: prometheus-mcp-server [--prometheus-url URL]")
        print("Environment: PROMETHEUS_URL (default: http://localhost:9090)")
        return
    
    # URL override
    if "--prometheus-url" in sys.argv:
        try:
            idx = sys.argv.index("--prometheus-url")
            if idx + 1 < len(sys.argv):
                global PROMETHEUS_URL
                PROMETHEUS_URL = sys.argv[idx + 1]
                # Recreate client with new URL
                global prometheus
                prometheus = PrometheusClient(PROMETHEUS_URL, PROMETHEUS_TIMEOUT)
        except (IndexError, ValueError):
            print("Error: --prometheus-url requires a URL")
            sys.exit(1)
    
    run_server()


if __name__ == "__main__":
    main()