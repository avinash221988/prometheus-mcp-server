"""
Kubernetes MCP Server - Provides tools for interacting with Kubernetes clusters.

This server complements the Prometheus MCP by providing Kubernetes-specific operations
for diagnostics, remediation, and cluster management.
"""

import os
import json
from typing import Any, Dict, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
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

# Initialize MCP server
app = Server("kubernetes-mcp-server")


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
            
            # Container state
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

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Kubernetes tools."""
    return [
        Tool(
            name="k8s_get_pod",
            description="Get detailed information about a specific pod",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Pod name"},
                    "namespace": {"type": "string", "description": "Namespace (default: default)"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="k8s_list_pods",
            description="List pods in a namespace with optional label selector",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace (default: all)"},
                    "label_selector": {"type": "string", "description": "Label selector (e.g., app=nginx)"}
                }
            }
        ),
        Tool(
            name="k8s_get_pod_logs",
            description="Get logs from a pod container",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Pod name"},
                    "namespace": {"type": "string", "description": "Namespace (default: default)"},
                    "container": {"type": "string", "description": "Container name (optional)"},
                    "tail_lines": {"type": "integer", "description": "Number of lines to tail (default: 100)"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="k8s_get_events",
            description="Get events for a pod or namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace"},
                    "pod_name": {"type": "string", "description": "Filter by pod name (optional)"}
                },
                "required": ["namespace"]
            }
        ),
        Tool(
            name="k8s_delete_pod",
            description="Delete a pod (useful for forcing recreation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Pod name"},
                    "namespace": {"type": "string", "description": "Namespace (default: default)"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="k8s_get_deployment",
            description="Get deployment information",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Deployment name"},
                    "namespace": {"type": "string", "description": "Namespace (default: default)"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="k8s_scale_deployment",
            description="Scale a deployment to a specific number of replicas",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Deployment name"},
                    "namespace": {"type": "string", "description": "Namespace (default: default)"},
                    "replicas": {"type": "integer", "description": "Number of replicas"}
                },
                "required": ["name", "replicas"]
            }
        ),
        Tool(
            name="k8s_restart_deployment",
            description="Restart a deployment by updating its annotation",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Deployment name"},
                    "namespace": {"type": "string", "description": "Namespace (default: default)"}
                },
                "required": ["name"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""

    try:
        if name == "k8s_get_pod":
            return await get_pod(arguments)
        elif name == "k8s_list_pods":
            return await list_pods(arguments)
        elif name == "k8s_get_pod_logs":
            return await get_pod_logs(arguments)
        elif name == "k8s_get_events":
            return await get_events(arguments)
        elif name == "k8s_delete_pod":
            return await delete_pod(arguments)
        elif name == "k8s_get_deployment":
            return await get_deployment(arguments)
        elif name == "k8s_scale_deployment":
            return await scale_deployment(arguments)
        elif name == "k8s_restart_deployment":
            return await restart_deployment(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# ============================================================================
# Tool Implementations
# ============================================================================

async def get_pod(args: Dict[str, Any]) -> list[TextContent]:
    """Get detailed pod information."""
    name = args["name"]
    namespace = args.get("namespace", "default")

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

        return [TextContent(
            type="text",
            text=json.dumps(status, indent=2)
        )]

    except ApiException as e:
        return [TextContent(
            type="text",
            text=f"Error getting pod: {e.reason}"
        )]


async def list_pods(args: Dict[str, Any]) -> list[TextContent]:
    """List pods in namespace."""
    namespace = args.get("namespace")
    label_selector = args.get("label_selector")

    try:
        if namespace:
            pods = v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector
            )
        else:
            pods = v1.list_pod_for_all_namespaces(
                label_selector=label_selector
            )

        pod_list = []
        for pod in pods.items:
            pod_list.append({
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "phase": pod.status.phase,
                "ready": sum(1 for c in (pod.status.container_statuses or []) if c.ready),
                "total": len(pod.status.container_statuses or []),
                "restarts": sum(c.restart_count for c in (pod.status.container_statuses or [])),
                "node": pod.spec.node_name
            })

        return [TextContent(
            type="text",
            text=json.dumps(pod_list, indent=2)
        )]

    except ApiException as e:
        return [TextContent(
            type="text",
            text=f"Error listing pods: {e.reason}"
        )]


async def get_pod_logs(args: Dict[str, Any]) -> list[TextContent]:
    """Get pod logs."""
    name = args["name"]
    namespace = args.get("namespace", "default")
    container = args.get("container")
    tail_lines = args.get("tail_lines", 100)

    try:
        logs = v1.read_namespaced_pod_log(
            name=name,
            namespace=namespace,
            container=container,
            tail_lines=tail_lines
        )

        return [TextContent(
            type="text",
            text=f"Logs for pod {name} (last {tail_lines} lines):\n\n{logs}"
        )]

    except ApiException as e:
        return [TextContent(
            type="text",
            text=f"Error getting logs: {e.reason}"
        )]


async def get_events(args: Dict[str, Any]) -> list[TextContent]:
    """Get Kubernetes events."""
    namespace = args["namespace"]
    pod_name = args.get("pod_name")

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
                "object": f"{event.involved_object.kind}/{event.involved_object.name}",
                "count": event.count,
                "first_seen": str(event.first_timestamp),
                "last_seen": str(event.last_timestamp)
            })

        # Sort by last_seen (most recent first)
        event_list.sort(key=lambda x: x["last_seen"], reverse=True)

        return [TextContent(
            type="text",
            text=json.dumps(event_list, indent=2)
        )]

    except ApiException as e:
        return [TextContent(
            type="text",
            text=f"Error getting events: {e.reason}"
        )]


async def delete_pod(args: Dict[str, Any]) -> list[TextContent]:
    """Delete a pod."""
    name = args["name"]
    namespace = args.get("namespace", "default")

    try:
        v1.delete_namespaced_pod(name=name, namespace=namespace)

        return [TextContent(
            type="text",
            text=f"Pod {name} in namespace {namespace} deleted successfully"
        )]

    except ApiException as e:
        return [TextContent(
            type="text",
            text=f"Error deleting pod: {e.reason}"
        )]


async def get_deployment(args: Dict[str, Any]) -> list[TextContent]:
    """Get deployment information."""
    name = args["name"]
    namespace = args.get("namespace", "default")

    try:
        deployment = apps_v1.read_namespaced_deployment(name=name, namespace=namespace)

        info = {
            "name": deployment.metadata.name,
            "namespace": deployment.metadata.namespace,
            "replicas": {
                "desired": deployment.spec.replicas,
                "current": deployment.status.replicas,
                "ready": deployment.status.ready_replicas,
                "available": deployment.status.available_replicas,
                "unavailable": deployment.status.unavailable_replicas
            },
            "strategy": deployment.spec.strategy.type,
            "conditions": []
        }

        if deployment.status.conditions:
            for condition in deployment.status.conditions:
                info["conditions"].append({
                    "type": condition.type,
                    "status": condition.status,
                    "reason": condition.reason,
                    "message": condition.message
                })

        return [TextContent(
            type="text",
            text=json.dumps(info, indent=2)
        )]

    except ApiException as e:
        return [TextContent(
            type="text",
            text=f"Error getting deployment: {e.reason}"
        )]


async def scale_deployment(args: Dict[str, Any]) -> list[TextContent]:
    """Scale a deployment."""
    name = args["name"]
    namespace = args.get("namespace", "default")
    replicas = args["replicas"]

    try:
        # Get current deployment
        deployment = apps_v1.read_namespaced_deployment(name=name, namespace=namespace)

        # Update replicas
        deployment.spec.replicas = replicas

        # Patch deployment
        apps_v1.patch_namespaced_deployment(
            name=name,
            namespace=namespace,
            body=deployment
        )

        return [TextContent(
            type="text",
            text=f"Deployment {name} scaled to {replicas} replicas"
        )]

    except ApiException as e:
        return [TextContent(
            type="text",
            text=f"Error scaling deployment: {e.reason}"
        )]


async def restart_deployment(args: Dict[str, Any]) -> list[TextContent]:
    """Restart a deployment by updating its annotation."""
    name = args["name"]
    namespace = args.get("namespace", "default")

    try:
        from datetime import datetime, timezone

        # Get current deployment
        deployment = apps_v1.read_namespaced_deployment(name=name, namespace=namespace)

        # Update restart annotation
        if not deployment.spec.template.metadata.annotations:
            deployment.spec.template.metadata.annotations = {}

        deployment.spec.template.metadata.annotations["kubectl.kubernetes.io/restartedAt"] = \
            datetime.now(timezone.utc).isoformat()

        # Patch deployment
        apps_v1.patch_namespaced_deployment(
            name=name,
            namespace=namespace,
            body=deployment
        )

        return [TextContent(
            type="text",
            text=f"Deployment {name} restarted successfully"
        )]

    except ApiException as e:
        return [TextContent(
            type="text",
            text=f"Error restarting deployment: {e.reason}"
        )]


# ============================================================================
# Main
# ============================================================================

async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

