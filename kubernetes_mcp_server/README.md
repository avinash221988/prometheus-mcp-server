# Kubernetes MCP Server

MCP server for interacting with Kubernetes clusters. Provides tools for diagnostics, remediation, and cluster management.

## Features

### Pod Management
- **k8s_get_pod** - Get detailed pod information including status, conditions, and events
- **k8s_list_pods** - List pods with optional label selectors
- **k8s_get_pod_logs** - Retrieve pod logs for debugging
- **k8s_delete_pod** - Delete a pod (useful for forcing recreation)

### Deployment Management
- **k8s_get_deployment** - Get deployment status and replica information
- **k8s_scale_deployment** - Scale deployments up or down
- **k8s_restart_deployment** - Restart a deployment (rolling restart)

### Diagnostics
- **k8s_get_events** - Get Kubernetes events for troubleshooting

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

The server uses your local kubeconfig by default (`~/.kube/config`). It will automatically detect:
- In-cluster configuration (when running inside Kubernetes)
- Local kubeconfig (for development)

## Usage with Augment

Add to your VS Code settings (`.vscode/settings.json` or User Settings):

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "/path/to/venv/bin/python3",
      "args": ["-m", "kubernetes_mcp_server.server"]
    }
  }
}
```

## Integration with Prometheus MCP

This server is designed to work alongside the Prometheus MCP server for holistic incident response:

1. **Prometheus MCP** - Detects alerts and monitors metrics
2. **Kubernetes MCP** - Provides detailed diagnostics and remediation

### Example Workflow

```
Alert: RegistryAdapterPodNotRunning
  ↓
Prometheus MCP: Get alert details
  ↓
Kubernetes MCP: Get pod status and events
  ↓
Kubernetes MCP: Get pod logs
  ↓
Prometheus MCP: Check related metrics (ECR proxy)
  ↓
Kubernetes MCP: Restart failed deployment
  ↓
Prometheus MCP: Verify alert cleared
```

## Available Tools

### k8s_get_pod
Get detailed information about a specific pod.

**Parameters:**
- `name` (required): Pod name
- `namespace` (optional): Namespace (default: "default")

**Returns:**
- Pod phase, conditions, container statuses, events

### k8s_list_pods
List pods in a namespace.

**Parameters:**
- `namespace` (optional): Namespace (default: all namespaces)
- `label_selector` (optional): Label selector (e.g., "app=nginx")

**Returns:**
- List of pods with name, namespace, phase, ready count, restarts

### k8s_get_pod_logs
Get logs from a pod container.

**Parameters:**
- `name` (required): Pod name
- `namespace` (optional): Namespace (default: "default")
- `container` (optional): Container name (for multi-container pods)
- `tail_lines` (optional): Number of lines to tail (default: 100)

**Returns:**
- Pod logs

### k8s_get_events
Get Kubernetes events.

**Parameters:**
- `namespace` (required): Namespace
- `pod_name` (optional): Filter by pod name

**Returns:**
- List of events with type, reason, message, timestamps

### k8s_delete_pod
Delete a pod (useful for forcing recreation).

**Parameters:**
- `name` (required): Pod name
- `namespace` (optional): Namespace (default: "default")

**Returns:**
- Confirmation message

### k8s_get_deployment
Get deployment information.

**Parameters:**
- `name` (required): Deployment name
- `namespace` (optional): Namespace (default: "default")

**Returns:**
- Deployment status, replica counts, conditions

### k8s_scale_deployment
Scale a deployment.

**Parameters:**
- `name` (required): Deployment name
- `namespace` (optional): Namespace (default: "default")
- `replicas` (required): Number of replicas

**Returns:**
- Confirmation message

### k8s_restart_deployment
Restart a deployment (rolling restart).

**Parameters:**
- `name` (required): Deployment name
- `namespace` (optional): Namespace (default: "default")

**Returns:**
- Confirmation message

## Security Considerations

This server requires appropriate Kubernetes RBAC permissions:

- **Read permissions**: pods, deployments, events
- **Write permissions**: pods (delete), deployments (patch)

Make sure your kubeconfig has the necessary permissions for the operations you want to perform.

## License

MIT

