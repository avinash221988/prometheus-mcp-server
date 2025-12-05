"""
Kubernetes MCP Server - Provides tools for interacting with Kubernetes clusters.

This server complements the Prometheus MCP by providing Kubernetes-specific operations
for diagnostics, remediation, and cluster management.
"""

import json
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from fastmcp import FastMCP
from kubernetes import client, config
from kubernetes.client.rest import ApiException


# Initialize Kubernetes client
try:
    # Try in-cluster config first (for running inside K8s)
    config.load_incluster_config()
except:
    # Fall back to kubeconfig (for local development)
    config.load_kube_config()

# Kubernetes API clients
v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()

# Create FastMCP app
mcp = FastMCP("Kubernetes MCP Server")


# ============================================================================
# Helper Functions
# ============================================================================

def format_pod_status(pod: Any) -> Dict[str, Any]:
    """Format pod status into a readable structure."""
    status = {
        "name": pod.metadata.name,
        "namespace": pod.metadata.namespace,
        "phase": pod.status.phase,
        "conditions": [],
        "container_statuses": [],
        "events": []
    }
    
    # Pod conditions
    if pod.status.conditions:
        for condition in pod.status.conditions:
            status["conditions"].append({
                "type": condition.type,
                "status": condition.status,
                "reason": condition.reason,
                "message": condition.message
            })
    
    # Container statuses
    if pod.status.container_statuses:
        for container in pod.status.container_statuses:
            container_info = {
                "name": container.name,
                "ready": container.ready,
                "restart_count": container.restart_count,
                "image": container.image
            }
            
            if container.state.waiting:
                container_info["state"] = "waiting"
                container_info["reason"] = container.state.waiting.reason
                container_info["message"] = container.state.waiting.message
            elif container.state.running:
                container_info["state"] = "running"
                container_info["started_at"] = str(container.state.running.started_at)
            elif container.state.terminated:
                container_info["state"] = "terminated"
                container_info["reason"] = container.state.terminated.reason
                container_info["exit_code"] = container.state.terminated.exit_code
            
            status["container_statuses"].append(container_info)
    
    return status


# ============================================================================
# MCP Tools
# ============================================================================

@mcp.tool()
async def k8s_get_pod(name: str, namespace: str = "default") -> str:
    """Get detailed information about a specific pod including status, conditions, and events.
    
    Args:
        name: Pod name
        namespace: Namespace (default: default)
    
    Returns:
        JSON string with pod details, status, conditions, container statuses, and events
    """
    try:
        pod = v1.read_namespaced_pod(name=name, namespace=namespace)
        status = format_pod_status(pod)
        
        # Get events for this pod
        events = v1.list_namespaced_event(
            namespace=namespace,
            field_selector=f"involvedObject.name={name}"
        )
        
        for event in events.items:
            status["events"].append({
                "type": event.type,
                "reason": event.reason,
                "message": event.message,
                "count": event.count,
                "first_timestamp": str(event.first_timestamp),
                "last_timestamp": str(event.last_timestamp)
            })
        
        return json.dumps(status, indent=2)
    except ApiException as e:
        return json.dumps({"error": f"Failed to get pod: {e.reason}"}, indent=2)


@mcp.tool()
async def k8s_list_pods(namespace: Optional[str] = None, label_selector: Optional[str] = None) -> str:
    """List pods in a namespace with optional label selector.
    
    Args:
        namespace: Namespace (default: all namespaces)
        label_selector: Label selector (e.g., app=nginx)
    
    Returns:
        JSON string with list of pods and their basic status
    """
    try:
        if namespace:
            pods = v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector or ""
            )
        else:
            pods = v1.list_pod_for_all_namespaces(
                label_selector=label_selector or ""
            )
        
        pod_list = []
        for pod in pods.items:
            pod_info = {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "phase": pod.status.phase,
                "ready": "0/0",
                "restarts": 0
            }
            
            if pod.status.container_statuses:
                ready_count = sum(1 for c in pod.status.container_statuses if c.ready)
                total_count = len(pod.status.container_statuses)
                pod_info["ready"] = f"{ready_count}/{total_count}"
                pod_info["restarts"] = sum(c.restart_count for c in pod.status.container_statuses)
            
            pod_list.append(pod_info)
        
        return json.dumps(pod_list, indent=2)
    except ApiException as e:
        return json.dumps({"error": f"Failed to list pods: {e.reason}"}, indent=2)


@mcp.tool()
async def k8s_get_pod_logs(
    name: str,
    namespace: str = "default",
    container: Optional[str] = None,
    tail_lines: int = 100
) -> str:
    """Get logs from a pod container.

    Args:
        name: Pod name
        namespace: Namespace (default: default)
        container: Container name (optional, uses first container if not specified)
        tail_lines: Number of lines to tail (default: 100)

    Returns:
        Pod logs as a string
    """
    try:
        logs = v1.read_namespaced_pod_log(
            name=name,
            namespace=namespace,
            container=container,
            tail_lines=tail_lines
        )
        return f"Logs for pod {name} (last {tail_lines} lines):\n\n{logs}"
    except ApiException as e:
        return f"Error getting logs: {e.reason}"


@mcp.tool()
async def k8s_get_events(namespace: str, pod_name: Optional[str] = None) -> str:
    """Get events for a pod or namespace.

    Args:
        namespace: Namespace
        pod_name: Filter by pod name (optional)

    Returns:
        JSON string with events
    """
    try:
        if pod_name:
            events = v1.list_namespaced_event(
                namespace=namespace,
                field_selector=f"involvedObject.name={pod_name}"
            )
        else:
            events = v1.list_namespaced_event(namespace=namespace)

        event_list = []
        for event in events.items:
            event_list.append({
                "type": event.type,
                "reason": event.reason,
                "message": event.message,
                "count": event.count,
                "first_timestamp": str(event.first_timestamp),
                "last_timestamp": str(event.last_timestamp),
                "involved_object": {
                    "kind": event.involved_object.kind,
                    "name": event.involved_object.name
                }
            })

        return json.dumps(event_list, indent=2)
    except ApiException as e:
        return json.dumps({"error": f"Failed to get events: {e.reason}"}, indent=2)


@mcp.tool()
async def k8s_delete_pod(name: str, namespace: str = "default") -> str:
    """Delete a pod (useful for forcing recreation).

    Args:
        name: Pod name
        namespace: Namespace (default: default)

    Returns:
        Success or error message
    """
    try:
        v1.delete_namespaced_pod(name=name, namespace=namespace)
        return f"Pod {name} in namespace {namespace} deleted successfully"
    except ApiException as e:
        return f"Error deleting pod: {e.reason}"


@mcp.tool()
async def k8s_get_deployment(name: str, namespace: str = "default") -> str:
    """Get deployment information including replica status.

    Args:
        name: Deployment name
        namespace: Namespace (default: default)

    Returns:
        JSON string with deployment details
    """
    try:
        deployment = apps_v1.read_namespaced_deployment(name=name, namespace=namespace)

        deployment_info = {
            "name": deployment.metadata.name,
            "namespace": deployment.metadata.namespace,
            "replicas": {
                "desired": deployment.spec.replicas,
                "current": deployment.status.replicas or 0,
                "ready": deployment.status.ready_replicas or 0,
                "available": deployment.status.available_replicas or 0,
                "unavailable": deployment.status.unavailable_replicas or 0
            },
            "strategy": deployment.spec.strategy.type,
            "conditions": []
        }

        if deployment.status.conditions:
            for condition in deployment.status.conditions:
                deployment_info["conditions"].append({
                    "type": condition.type,
                    "status": condition.status,
                    "reason": condition.reason,
                    "message": condition.message
                })

        return json.dumps(deployment_info, indent=2)
    except ApiException as e:
        return json.dumps({"error": f"Failed to get deployment: {e.reason}"}, indent=2)


@mcp.tool()
async def k8s_scale_deployment(name: str, namespace: str = "default", replicas: int = 1) -> str:
    """Scale a deployment to a specific number of replicas.

    Args:
        name: Deployment name
        namespace: Namespace (default: default)
        replicas: Number of replicas

    Returns:
        Success or error message
    """
    try:
        deployment = apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
        deployment.spec.replicas = replicas

        apps_v1.patch_namespaced_deployment(
            name=name,
            namespace=namespace,
            body=deployment
        )

        return f"Deployment {name} scaled to {replicas} replicas"
    except ApiException as e:
        return f"Error scaling deployment: {e.reason}"


@mcp.tool()
async def k8s_restart_deployment(name: str, namespace: str = "default") -> str:
    """Restart a deployment by updating its annotation (rolling restart).

    Args:
        name: Deployment name
        namespace: Namespace (default: default)

    Returns:
        Success or error message
    """
    try:
        deployment = apps_v1.read_namespaced_deployment(name=name, namespace=namespace)

        if not deployment.spec.template.metadata.annotations:
            deployment.spec.template.metadata.annotations = {}

        deployment.spec.template.metadata.annotations["kubectl.kubernetes.io/restartedAt"] = \
            datetime.now(timezone.utc).isoformat()

        apps_v1.patch_namespaced_deployment(
            name=name,
            namespace=namespace,
            body=deployment
        )

        return f"Deployment {name} restarted successfully"
    except ApiException as e:
        return f"Error restarting deployment: {e.reason}"


def main():
    """Run the Kubernetes MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
