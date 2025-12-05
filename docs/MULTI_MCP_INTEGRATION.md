# Multi-MCP Integration Guide: Prometheus + Kubernetes

This guide explains how to use Prometheus MCP and Kubernetes MCP together for holistic incident response and cluster management.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Assistant (Augment)                    │
│  Orchestrates tools from multiple MCP servers                │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──────────────────────┬──────────────────────────┐
             │                      │                          │
             ▼                      ▼                          ▼
    ┌────────────────┐    ┌────────────────┐       ┌────────────────┐
    │ Prometheus MCP │    │ Kubernetes MCP │       │  Future MCPs   │
    │                │    │                │       │                │
    │ - Monitoring   │    │ - Diagnostics  │       │ - GitOps       │
    │ - Alerting     │    │ - Remediation  │       │ - Logging      │
    │ - Metrics      │    │ - Management   │       │ - Tracing      │
    └────────────────┘    └────────────────┘       └────────────────┘
```

## Setup

### 1. Configure Both MCP Servers

Add both servers to your VS Code settings (`.vscode/settings.json`):

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "/Users/abh551/prometheus-mcp-server/venv/bin/python3",
      "args": ["-m", "prometheus_mcp_server.simple_server"],
      "env": {
        "PROMETHEUS_URL": "https://platform-prometheus.sandpfm.cosmic.sky",
        "ALERTMANAGER_URL": "https://platform-alertmanager.sandpfm.cosmic.sky/",
        "PROMETHEUS_TIMEOUT": "30",
        "VERIFY_SSL": "false"
      }
    },
    "kubernetes": {
      "command": "/Users/abh551/prometheus-mcp-server/venv/bin/python3",
      "args": ["-m", "kubernetes_mcp_server.server"]
    }
  }
}
```

### 2. Install Dependencies

```bash
# Prometheus MCP (already installed)
cd /Users/abh551/prometheus-mcp-server
source venv/bin/activate
pip install -r requirements.txt

# Kubernetes MCP (new)
pip install -r kubernetes_mcp_server/requirements.txt
```

### 3. Verify Kubernetes Access

```bash
# Test kubectl access
kubectl get pods --all-namespaces

# Verify kubeconfig
kubectl config current-context
```

### 4. Reload VS Code

After configuration, reload VS Code to activate both MCP servers.

## Use Cases

### Use Case 1: Alert Investigation

**Scenario:** Pod is failing, need to diagnose why.

**Workflow:**
```
1. Prometheus MCP: Get firing alerts
   → alertmanager_get_alerts()
   
2. Identify critical alert: "RegistryAdapterPodNotRunning"

3. Prometheus MCP: Query pod metrics
   → prometheus_query('kube_pod_status_phase{pod="registry-adapter-7875bffcb4-kkxlw"}')
   
4. Kubernetes MCP: Get detailed pod info
   → k8s_get_pod(name="registry-adapter-7875bffcb4-kkxlw", namespace="registry-adapter-stubbed-showcase")
   
5. Kubernetes MCP: Get pod events
   → k8s_get_events(namespace="registry-adapter-stubbed-showcase", pod_name="registry-adapter-7875bffcb4-kkxlw")
   
6. Kubernetes MCP: Get pod logs
   → k8s_get_pod_logs(name="registry-adapter-7875bffcb4-kkxlw", namespace="registry-adapter-stubbed-showcase")
   
7. Analyze: "ImagePullBackOff - Failed to pull image from ECR"

8. Prometheus MCP: Check ECR proxy metrics
   → prometheus_query('kube_deployment_status_replicas{deployment="ecr-proxy"}')
   
9. Root cause: ECR proxy is down
```

### Use Case 2: Automated Remediation

**Scenario:** Deployment has insufficient replicas, need to scale up.

**Workflow:**
```
1. Prometheus MCP: Get alert
   → "ArgocdApplicationInsufficientReplicas"
   
2. Kubernetes MCP: Get deployment status
   → k8s_get_deployment(name="argocd-server", namespace="argocd")
   
3. Analyze: Desired=3, Available=1

4. Kubernetes MCP: Scale deployment
   → k8s_scale_deployment(name="argocd-server", namespace="argocd", replicas=3)
   
5. Wait 30 seconds

6. Prometheus MCP: Verify alert cleared
   → alertmanager_get_alerts()
```

### Use Case 3: Deployment Restart

**Scenario:** Application is stuck, need to restart.

**Workflow:**
```
1. Prometheus MCP: Identify unhealthy service
   → prometheus_services()
   
2. Kubernetes MCP: Get deployment info
   → k8s_get_deployment(name="my-app", namespace="production")
   
3. Kubernetes MCP: Restart deployment
   → k8s_restart_deployment(name="my-app", namespace="production")
   
4. Kubernetes MCP: Monitor pod recreation
   → k8s_list_pods(namespace="production", label_selector="app=my-app")
   
5. Prometheus MCP: Verify metrics recovered
   → prometheus_query('up{job="my-app"}')
```

## Common Patterns

### Pattern 1: Alert → Diagnose → Remediate → Verify

```python
# 1. Get alerts (Prometheus MCP)
alerts = alertmanager_get_alerts()

# 2. Diagnose (Kubernetes MCP)
pod_info = k8s_get_pod(name=pod_name, namespace=namespace)
events = k8s_get_events(namespace=namespace, pod_name=pod_name)
logs = k8s_get_pod_logs(name=pod_name, namespace=namespace)

# 3. Remediate (Kubernetes MCP)
k8s_delete_pod(name=pod_name, namespace=namespace)  # Force recreation
# OR
k8s_restart_deployment(name=deployment_name, namespace=namespace)

# 4. Verify (Prometheus MCP)
# Wait for alert to clear
alerts_after = alertmanager_get_alerts()
```

### Pattern 2: Metrics → Pods → Logs

```python
# 1. Check metrics (Prometheus MCP)
cpu_usage = prometheus_query('container_cpu_usage_seconds_total{pod=~"my-app.*"}')

# 2. Find high CPU pods (Kubernetes MCP)
pods = k8s_list_pods(namespace="production", label_selector="app=my-app")

# 3. Get logs from problematic pods (Kubernetes MCP)
for pod in high_cpu_pods:
    logs = k8s_get_pod_logs(name=pod["name"], namespace=pod["namespace"], tail_lines=500)
```

### Pattern 3: Correlation Analysis

```python
# 1. Get all firing alerts (Prometheus MCP)
alerts = alertmanager_get_alerts()

# 2. For each alert, get Kubernetes context (Kubernetes MCP)
for alert in alerts:
    if "pod" in alert["labels"]:
        pod_info = k8s_get_pod(
            name=alert["labels"]["pod"],
            namespace=alert["labels"]["namespace"]
        )
        events = k8s_get_events(
            namespace=alert["labels"]["namespace"],
            pod_name=alert["labels"]["pod"]
        )

# 3. Correlate: Find common root causes
# Example: Multiple pods failing due to same image pull issue
```

## Best Practices

### 1. Always Verify Before Remediation
```python
# ❌ Bad: Immediate action
k8s_delete_pod(name=pod_name, namespace=namespace)

# ✅ Good: Investigate first
pod_info = k8s_get_pod(name=pod_name, namespace=namespace)
events = k8s_get_events(namespace=namespace, pod_name=pod_name)
# Analyze, then decide
if should_delete:
    k8s_delete_pod(name=pod_name, namespace=namespace)
```

### 2. Use Both Data Sources
```python
# Prometheus: High-level metrics and trends
# Kubernetes: Detailed state and events

# Get both perspectives
metrics = prometheus_query('kube_pod_status_phase{...}')  # Prometheus view
pod_info = k8s_get_pod(name=pod_name, namespace=namespace)  # Kubernetes view
```

### 3. Silence Alerts During Remediation
```python
# 1. Silence alert (Prometheus MCP)
alertmanager_silence(
    alert_name="MyAlert",
    duration="30m",
    reason="Performing remediation"
)

# 2. Perform remediation (Kubernetes MCP)
k8s_restart_deployment(name=deployment_name, namespace=namespace)

# 3. Wait and verify
# 4. Alert will auto-clear when silence expires
```

## Advantages of Multi-MCP Architecture

### 1. **Separation of Concerns**
- Prometheus MCP: Monitoring domain
- Kubernetes MCP: Orchestration domain
- Each server is focused and maintainable

### 2. **Composability**
- AI assistant can combine tools from both servers
- Create complex workflows without modifying servers
- Add new MCP servers without changing existing ones

### 3. **Reusability**
- Kubernetes MCP can be used independently
- Prometheus MCP can work with other orchestrators
- Tools are modular and composable

### 4. **Holistic View**
- Metrics + Events + Logs + State
- Time-series data + Point-in-time snapshots
- Monitoring + Diagnostics + Remediation

### 5. **Flexibility**
- AI decides which tools to use and when
- No hard-coded workflows
- Adapts to different scenarios

## Future Enhancements

### Additional MCP Servers
- **GitOps MCP** - ArgoCD, Flux integration
- **Logging MCP** - Loki, Elasticsearch integration
- **Tracing MCP** - Jaeger, Tempo integration
- **Cloud MCP** - AWS, GCP, Azure integration

### Enhanced Kubernetes MCP
- ConfigMap/Secret management
- Service/Ingress management
- StatefulSet operations
- Job/CronJob management
- RBAC inspection

### Enhanced Prometheus MCP
- Recording rules management
- Alert rule management
- Grafana dashboard integration
- Long-term metrics analysis

## Troubleshooting

### Kubernetes MCP Not Working

```bash
# Check kubeconfig
kubectl config current-context

# Test kubectl access
kubectl get pods --all-namespaces

# Check Python Kubernetes client
python3 -c "from kubernetes import client, config; config.load_kube_config(); print('OK')"
```

### Permission Errors

```bash
# Check RBAC permissions
kubectl auth can-i get pods --all-namespaces
kubectl auth can-i delete pods --all-namespaces
kubectl auth can-i patch deployments --all-namespaces
```

### Both MCPs Not Loading

```bash
# Reload VS Code
# Check MCP server logs in VS Code Output panel
# Verify both servers are configured correctly in settings.json
```

## Example: Complete Incident Response

```
User: "ArgoCD is down, please investigate and fix"

AI Assistant:
  ↓
1. Prometheus MCP: Get ArgoCD alerts
   → 6 alerts: ArgocdApplicationNotRunning, ArgocdApplicationInsufficientReplicas
   
2. Kubernetes MCP: List ArgoCD pods
   → k8s_list_pods(namespace="argocd", label_selector="app.kubernetes.io/name=argocd")
   → Found 5 pods, 3 are not ready
   
3. Kubernetes MCP: Get details on failing pods
   → k8s_get_pod(name="argocd-server-7986665999-8ms45", namespace="argocd")
   → Status: CrashLoopBackOff
   
4. Kubernetes MCP: Get events
   → k8s_get_events(namespace="argocd", pod_name="argocd-server-7986665999-8ms45")
   → "Back-off restarting failed container"
   
5. Kubernetes MCP: Get logs
   → k8s_get_pod_logs(name="argocd-server-7986665999-8ms45", namespace="argocd", tail_lines=200)
   → "Failed to connect to Redis: connection refused"
   
6. Prometheus MCP: Check Redis metrics
   → prometheus_query('up{job="redis",namespace="argocd"}')
   → Redis is down!
   
7. Kubernetes MCP: Check Redis deployment
   → k8s_get_deployment(name="argocd-redis", namespace="argocd")
   → 0/1 replicas available
   
8. Kubernetes MCP: Restart Redis
   → k8s_restart_deployment(name="argocd-redis", namespace="argocd")
   
9. Wait 30 seconds...

10. Kubernetes MCP: Verify Redis is up
    → k8s_list_pods(namespace="argocd", label_selector="app=redis")
    → Redis pod is Running
    
11. Kubernetes MCP: Verify ArgoCD pods recovered
    → k8s_list_pods(namespace="argocd", label_selector="app.kubernetes.io/name=argocd")
    → All pods are Running
    
12. Prometheus MCP: Verify alerts cleared
    → alertmanager_get_alerts()
    → ArgoCD alerts cleared!

AI: "Root cause was Redis being down. I restarted the Redis deployment and all ArgoCD pods recovered. All alerts have cleared."
```

This is the power of multi-MCP architecture! 🚀

