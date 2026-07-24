"""
Kubernetes MCP Server

A FastMCP-based server for Kubernetes cluster operations.
Provides resources, tools, and prompts for K8s management.
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastmcp import FastMCP
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Configuration from environment
K8S_CONTEXT = os.getenv("K8S_CONTEXT", "")  # Empty means use current context
K8S_NAMESPACE = os.getenv("K8S_NAMESPACE", "default")

# Create FastMCP app
mcp = FastMCP("Kubernetes MCP Server")


class KubernetesClient:
    """Kubernetes API client wrapper."""

    def __init__(self, context: str = "", namespace: str = "default"):
        self.context = context
        self.namespace = namespace
        self._load_config()

        # Initialize API clients
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.events_v1 = client.EventsV1Api()

    def _load_config(self):
        """Load kubeconfig with optional context."""
        try:
            if self.context:
                config.load_kube_config(context=self.context)
            else:
                config.load_kube_config()
        except Exception as e:
            # Fallback to in-cluster config if kubeconfig fails
            try:
                config.load_incluster_config()
            except Exception:
                raise Exception(f"Failed to load kubeconfig: {e}")

    def _handle_api_exception(self, e: ApiException) -> Dict[str, Any]:
        """Convert API exception to error dict."""
        return {
            "error": f"Kubernetes API error: {e.reason}",
            "status": e.status,
            "details": e.body
        }


# Global client instance
k8s = KubernetesClient(K8S_CONTEXT, K8S_NAMESPACE)


@mcp.resource("k8s://pods")
async def get_pods() -> str:
    """Get all pods in the current namespace."""
    try:
        pods = k8s.core_v1.list_namespaced_pod(namespace=k8s.namespace)
        return json.dumps(pods.to_dict(), indent=2, default=str)
    except ApiException as e:
        return json.dumps(k8s._handle_api_exception(e), indent=2)


@mcp.resource("k8s://pods/all")
async def get_all_pods() -> str:
    """Get all pods across all namespaces."""
    try:
        pods = k8s.core_v1.list_pod_for_all_namespaces()
        return json.dumps(pods.to_dict(), indent=2, default=str)
    except ApiException as e:
        return json.dumps(k8s._handle_api_exception(e), indent=2)


@mcp.resource("k8s://deployments")
async def get_deployments() -> str:
    """Get all deployments in the current namespace."""
    try:
        deployments = k8s.apps_v1.list_namespaced_deployment(namespace=k8s.namespace)
        return json.dumps(deployments.to_dict(), indent=2, default=str)
    except ApiException as e:
        return json.dumps(k8s._handle_api_exception(e), indent=2)


@mcp.resource("k8s://services")
async def get_services() -> str:
    """Get all services in the current namespace."""
    try:
        services = k8s.core_v1.list_namespaced_service(namespace=k8s.namespace)
        return json.dumps(services.to_dict(), indent=2, default=str)
    except ApiException as e:
        return json.dumps(k8s._handle_api_exception(e), indent=2)


@mcp.resource("k8s://nodes")
async def get_nodes() -> str:
    """Get all nodes in the cluster."""
    try:
        nodes = k8s.core_v1.list_node()
        return json.dumps(nodes.to_dict(), indent=2, default=str)
    except ApiException as e:
        return json.dumps(k8s._handle_api_exception(e), indent=2)


@mcp.resource("k8s://namespaces")
async def get_namespaces() -> str:
    """Get all namespaces in the cluster."""
    try:
        namespaces = k8s.core_v1.list_namespace()
        return json.dumps(namespaces.to_dict(), indent=2, default=str)
    except ApiException as e:
        return json.dumps(k8s._handle_api_exception(e), indent=2)


# ============================================================================
# TOOLS - Actions that can be performed
# ============================================================================

@mcp.tool()
async def k8s_get_pod_logs(pod_name: str, namespace: str = "", tail: int = 100) -> str:
    """
    Get logs from a specific pod.

    Args:
        pod_name: Name of the pod
        namespace: Namespace (uses default if not specified)
        tail: Number of lines to tail (default: 100)

    Returns:
        Pod logs
    """
    ns = namespace or k8s.namespace
    try:
        logs = k8s.core_v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=ns,
            tail_lines=tail
        )
        return logs
    except ApiException as e:
        return json.dumps(k8s._handle_api_exception(e), indent=2)
    except Exception as e:
        return f"Error getting logs: {e}"


@mcp.tool()
async def k8s_describe_pod(pod_name: str, namespace: str = "") -> str:
    """
    Describe a specific pod.

    Args:
        pod_name: Name of the pod
        namespace: Namespace (uses default if not specified)

    Returns:
        Pod description
    """
    ns = namespace or k8s.namespace
    try:
        pod = k8s.core_v1.read_namespaced_pod(name=pod_name, namespace=ns)

        # Format pod description similar to kubectl describe
        description = f"Name:                 {pod.metadata.name}\n"
        description += f"Namespace:            {pod.metadata.namespace}\n"
        description += f"Priority:             {pod.spec.priority or 0}\n"
        description += f"Priority Class Name:  {pod.spec.priority_class_name or 'default'}\n"
        description += f"Service Account:      {pod.spec.service_account_name or 'default'}\n"
        description += f"Node:                 {pod.spec.node_name or 'N/A'}\n"
        description += f"Start Time:           {pod.status.start_time}\n"
        description += f"Labels:               {pod.metadata.labels or {}}\n"
        description += f"Annotations:          {pod.metadata.annotations or '<none>'}\n"
        description += f"Status:               {pod.status.phase}\n"
        description += f"IP:                   {pod.status.pod_ip or 'N/A'}\n"

        if pod.status.pod_ips:
            description += "IPs:\n"
            for ip in pod.status.pod_ips:
                description += f"  IP:           {ip.ip}\n"

        if pod.metadata.owner_references:
            for owner in pod.metadata.owner_references:
                description += f"Controlled By:  {owner.kind}/{owner.name}\n"

        description += "Containers:\n"
        for container in pod.spec.containers:
            description += f"  {container.name}:\n"
            description += f"    Container ID:  {next((cs.container_id for cs in (pod.status.container_statuses or []) if cs.name == container.name), 'N/A')}\n"
            description += f"    Image:         {container.image}\n"
            description += f"    Image ID:      {next((cs.image_id for cs in (pod.status.container_statuses or []) if cs.name == container.name), 'N/A')}\n"
            if container.ports:
                for port in container.ports:
                    description += f"    Port:          {port.container_port}/{port.protocol}\n"
                    description += f"    Host Port:     {port.host_port or 0}/{port.protocol}\n"
            if container.args:
                description += f"    Args:\n"
                for arg in container.args:
                    description += f"      {arg}\n"

            # Get container status
            if pod.status.container_statuses:
                for cs in pod.status.container_statuses:
                    if cs.name == container.name:
                        description += f"    State:          {list(cs.state.to_dict().keys())[0] if cs.state else 'Unknown'}\n"
                        if cs.state and cs.state.running:
                            description += f"      Started:      {cs.state.running.started_at}\n"
                        description += f"    Ready:          {cs.ready}\n"
                        description += f"    Restart Count:  {cs.restart_count}\n"

            if container.resources:
                if container.resources.limits:
                    description += f"    Limits:\n"
                    for k, v in container.resources.limits.items():
                        description += f"      {k}:  {v}\n"
                if container.resources.requests:
                    description += f"    Requests:\n"
                    for k, v in container.resources.requests.items():
                        description += f"      {k}:        {v}\n"

            if container.liveness_probe:
                description += f"    Liveness:     {container.liveness_probe.to_dict()}\n"
            if container.environment:
                description += f"    Environment:  {container.environment or '<none>'}\n"
            if container.volume_mounts:
                description += f"    Mounts:\n"
                for vm in container.volume_mounts:
                    description += f"      {vm.mount_path} from {vm.name} ({'ro' if vm.read_only else 'rw'})\n"

        description += "Conditions:\n"
        if pod.status.conditions:
            description += "  Type              Status\n"
            for condition in pod.status.conditions:
                description += f"  {condition.type:17} {condition.status}\n"

        if pod.spec.volumes:
            description += "Volumes:\n"
            for volume in pod.spec.volumes:
                description += f"  {volume.name}:\n"
                vol_dict = volume.to_dict()
                for k, v in vol_dict.items():
                    if v and k != 'name':
                        description += f"    Type:        {k.replace('_', ' ').title()}\n"
                        if isinstance(v, dict):
                            for vk, vv in v.items():
                                description += f"    {vk.replace('_', ' ').title()}:  {vv}\n"

        description += f"QoS Class:                   {pod.status.qos_class or 'BestEffort'}\n"
        description += f"Node-Selectors:              {pod.spec.node_selector or '<none>'}\n"

        if pod.spec.tolerations:
            description += "Tolerations:                 "
            for tol in pod.spec.tolerations:
                description += f"{tol.key}:{tol.effect} op={tol.operator} "
                if tol.toleration_seconds:
                    description += f"for {tol.toleration_seconds}s"
                description += "\n                             "

        # Get events for this pod
        try:
            events = k8s.core_v1.list_namespaced_event(
                namespace=ns,
                field_selector=f"involvedObject.name={pod_name}"
            )
            if events.items:
                description += "\nEvents:\n"
                for event in events.items[-10:]:  # Last 10 events
                    description += f"  {event.type}: {event.reason} - {event.message}\n"
            else:
                description += "\nEvents:                      <none>\n"
        except:
            description += "\nEvents:                      <none>\n"

        return description
    except ApiException as e:
        return json.dumps(k8s._handle_api_exception(e), indent=2)
    except Exception as e:
        return f"Error describing pod: {e}"


@mcp.tool()
async def k8s_scale_deployment(deployment_name: str, replicas: int, namespace: str = "") -> str:
    """
    Scale a deployment to a specific number of replicas.

    Args:
        deployment_name: Name of the deployment
        replicas: Number of replicas
        namespace: Namespace (uses default if not specified)

    Returns:
        Result of the scale operation
    """
    ns = namespace or k8s.namespace
    try:
        # Patch the deployment with new replica count
        body = {"spec": {"replicas": replicas}}
        k8s.apps_v1.patch_namespaced_deployment_scale(
            name=deployment_name,
            namespace=ns,
            body=body
        )
        return f"deployment.apps/{deployment_name} scaled to {replicas} replicas"
    except ApiException as e:
        return json.dumps(k8s._handle_api_exception(e), indent=2)
    except Exception as e:
        return f"Error scaling deployment: {e}"


@mcp.tool()
async def k8s_restart_deployment(deployment_name: str, namespace: str = "") -> str:
    """
    Restart a deployment by triggering a rollout restart.

    Args:
        deployment_name: Name of the deployment
        namespace: Namespace (uses default if not specified)

    Returns:
        Result of the restart operation
    """
    ns = namespace or k8s.namespace
    try:
        # Trigger rollout restart by updating the restart annotation
        now = datetime.utcnow().isoformat() + "Z"
        body = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": now
                        }
                    }
                }
            }
        }
        k8s.apps_v1.patch_namespaced_deployment(
            name=deployment_name,
            namespace=ns,
            body=body
        )
        return f"deployment.apps/{deployment_name} restarted"
    except ApiException as e:
        return json.dumps(k8s._handle_api_exception(e), indent=2)
    except Exception as e:
        return f"Error restarting deployment: {e}"


@mcp.tool()
async def k8s_get_events(namespace: str = "", limit: int = 50) -> str:
    """
    Get recent events in a namespace.

    Args:
        namespace: Namespace (uses default if not specified)
        limit: Number of events to return (default: 50)

    Returns:
        Recent events in JSON format
    """
    ns = namespace or k8s.namespace
    try:
        events = k8s.core_v1.list_namespaced_event(namespace=ns)

        # Sort by last timestamp
        sorted_events = sorted(
            events.items,
            key=lambda e: e.last_timestamp or e.event_time or datetime.min,
            reverse=True
        )

        # Limit the number of events
        limited_events = sorted_events[:limit]

        # Format events
        result = {
            "items": [
                {
                    "type": e.type,
                    "reason": e.reason,
                    "message": e.message,
                    "object": f"{e.involved_object.kind}/{e.involved_object.name}",
                    "count": e.count,
                    "first_timestamp": str(e.first_timestamp) if e.first_timestamp else None,
                    "last_timestamp": str(e.last_timestamp) if e.last_timestamp else str(e.event_time),
                }
                for e in limited_events
            ]
        }

        return json.dumps(result, indent=2)
    except ApiException as e:
        return json.dumps(k8s._handle_api_exception(e), indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
async def k8s_get_pod_status(namespace: str = "") -> str:
    """
    Get a summary of pod statuses in a namespace.

    Args:
        namespace: Namespace (uses default if not specified)

    Returns:
        Summary of pod statuses
    """
    ns = namespace or k8s.namespace
    try:
        pods = k8s.core_v1.list_namespaced_pod(namespace=ns)

        # Summarize pod statuses
        summary = {
            "total": 0,
            "running": 0,
            "pending": 0,
            "failed": 0,
            "succeeded": 0,
            "unknown": 0,
            "pods": []
        }

        summary["total"] = len(pods.items)
        for pod in pods.items:
            status = pod.status.phase
            restarts = sum(
                cs.restart_count
                for cs in (pod.status.container_statuses or [])
            )

            pod_info = {
                "name": pod.metadata.name,
                "status": status,
                "restarts": restarts
            }
            summary["pods"].append(pod_info)

            if status == "Running":
                summary["running"] += 1
            elif status == "Pending":
                summary["pending"] += 1
            elif status == "Failed":
                summary["failed"] += 1
            elif status == "Succeeded":
                summary["succeeded"] += 1
            else:
                summary["unknown"] += 1

        return json.dumps(summary, indent=2)
    except ApiException as e:
        return json.dumps(k8s._handle_api_exception(e), indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


# ============================================================================
# PROMPTS - AI analysis templates
# ============================================================================

@mcp.prompt()
async def troubleshoot_pod_prompt(pod_name: str, namespace: str = "") -> str:
    """
    Generate a prompt for troubleshooting a problematic pod.

    Args:
        pod_name: Name of the pod to troubleshoot
        namespace: Namespace (uses default if not specified)

    Returns:
        Formatted prompt with pod details and troubleshooting instructions
    """
    ns = namespace or k8s.namespace

    # Get pod details
    pod_result = await k8s.run_command(["get", "pod", pod_name])

    # Get pod description
    describe_result = await k8s_describe_pod(pod_name, ns)

    # Get recent logs
    logs = await k8s_get_pod_logs(pod_name, ns, tail=50)

    # Get recent events
    events = await k8s_get_events(ns, limit=20)

    prompt = f"""# Kubernetes Pod Troubleshooting Analysis

## Pod Information
- **Name**: {pod_name}
- **Namespace**: {ns}

## Pod Details
```json
{json.dumps(pod_result, indent=2)}
```

## Pod Description
```
{describe_result}
```

## Recent Logs (last 50 lines)
```
{logs}
```

## Recent Events
```json
{events}
```

## Analysis Instructions
Please analyze the above information and provide:

1. **Current Status**: What is the current state of the pod?
2. **Issues Identified**: What problems or anomalies do you see?
3. **Root Cause**: What is likely causing the issue?
4. **Impact**: How does this affect the application?
5. **Recommended Actions**: What steps should be taken to resolve this?
6. **Prevention**: How can we prevent this in the future?

Focus on:
- Container status and restart counts
- Resource constraints (CPU, memory)
- Image pull issues
- Configuration problems
- Network connectivity
- Volume mount issues
"""

    return prompt


@mcp.prompt()
async def analyze_deployment_prompt(deployment_name: str, namespace: str = "") -> str:
    """
    Generate a prompt for analyzing a deployment's health and performance.

    Args:
        deployment_name: Name of the deployment
        namespace: Namespace (uses default if not specified)

    Returns:
        Formatted prompt with deployment analysis
    """
    ns = namespace or k8s.namespace

    # Get deployment details
    deployment_result = await k8s.run_command(["get", "deployment", deployment_name])

    # Get pods for this deployment
    pods_result = await k8s.run_command(["get", "pods", "-l", f"app={deployment_name}"])

    # Get events
    events = await k8s_get_events(ns, limit=30)

    prompt = f"""# Kubernetes Deployment Analysis

## Deployment Information
- **Name**: {deployment_name}
- **Namespace**: {ns}

## Deployment Details
```json
{json.dumps(deployment_result, indent=2)}
```

## Associated Pods
```json
{json.dumps(pods_result, indent=2)}
```

## Recent Events
```json
{events}
```

## Analysis Instructions
Please analyze this deployment and provide:

1. **Health Status**: Is the deployment healthy?
2. **Replica Status**: Are all replicas running as expected?
3. **Pod Distribution**: How are pods distributed across nodes?
4. **Recent Changes**: Any recent rollouts or updates?
5. **Performance Issues**: Any signs of performance problems?
6. **Recommendations**: Suggestions for optimization or fixes

Consider:
- Desired vs available replicas
- Pod restart patterns
- Resource utilization
- Update strategy
- Readiness and liveness probes
"""

    return prompt


@mcp.prompt()
async def cluster_health_prompt() -> str:
    """
    Generate a prompt for overall cluster health analysis.

    Returns:
        Formatted prompt with cluster-wide health information
    """
    # Get nodes
    nodes = await k8s.run_command(["get", "nodes"])

    # Get all pods
    all_pods = await k8s.run_command(["get", "pods"], all_namespaces=True)

    # Get namespaces
    namespaces = await k8s.run_command(["get", "namespaces"])

    prompt = f"""# Kubernetes Cluster Health Analysis

## Nodes
```json
{json.dumps(nodes, indent=2)}
```

## All Pods (All Namespaces)
```json
{json.dumps(all_pods, indent=2)}
```

## Namespaces
```json
{json.dumps(namespaces, indent=2)}
```

## Analysis Instructions
Please provide a comprehensive cluster health analysis:

1. **Node Health**: Are all nodes ready and healthy?
2. **Resource Capacity**: What is the overall resource utilization?
3. **Pod Distribution**: How are pods distributed across nodes?
4. **Problem Areas**: Which namespaces or workloads have issues?
5. **Capacity Planning**: Any capacity concerns?
6. **Recommendations**: Suggestions for cluster optimization

Focus on:
- Node conditions and resource pressure
- Pods in non-Running states
- High restart counts
- Resource requests vs limits
- Namespace resource usage
"""

    return prompt


def run_server():
    """Run the MCP server."""
    context_info = f" (context: {K8S_CONTEXT})" if K8S_CONTEXT else " (using current context)"
    print(f"Starting Kubernetes MCP Server{context_info}")
    print(f"Default namespace: {K8S_NAMESPACE}")
    mcp.run()


def main():
    """Handle command line and start server."""
    import sys

    # Simple help
    if len(sys.argv) > 1 and ("--help" in sys.argv or "-h" in sys.argv):
        print("Kubernetes MCP Server")
        print("Usage: k8s-mcp-server [OPTIONS]")
        print("\nOptions:")
        print("  --context CONTEXT      Kubernetes context to use")
        print("  --namespace NAMESPACE  Default namespace (default: default)")
        print("\nEnvironment Variables:")
        print("  K8S_CONTEXT, K8S_NAMESPACE")
        return

    run_server()


if __name__ == "__main__":
    main()
