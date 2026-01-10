# Multi-MCP Quick Reference

## Configuration

### VS Code Settings (`.vscode/settings.json`)

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "/Users/abh551/prometheus-mcp-server/venv/bin/python3",
      "args": ["-m", "prometheus_mcp_server.simple_server"],
      "env": {
        "PROMETHEUS_URL": "https://platform-prometheus.sandpfm.cosmic.sky",
        "ALERTMANAGER_URL": "https://platform-alertmanager.sandpfm.cosmic.sky/",
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

## Tool Cheat Sheet

### Prometheus MCP Tools

| Tool | Purpose | Common Use |
|------|---------|------------|
| `alertmanager_get_alerts()` | Get firing alerts | Start of investigation |
| `prometheus_query(query)` | Execute PromQL | Check metrics, trends |
| `alertmanager_silence(...)` | Silence alert | During remediation |
| `prometheus_services()` | Check service health | Quick health check |

### Kubernetes MCP Tools

| Tool | Purpose | Common Use |
|------|---------|------------|
| `k8s_get_pod(name, ns)` | Get pod details | Investigate failing pod |
| `k8s_list_pods(ns, labels)` | List pods | Find affected pods |
| `k8s_get_pod_logs(name, ns)` | Get logs | See error messages |
| `k8s_get_events(ns, pod)` | Get events | Understand what happened |
| `k8s_delete_pod(name, ns)` | Delete pod | Force recreation |
| `k8s_restart_deployment(name, ns)` | Restart deployment | Rolling restart |
| `k8s_scale_deployment(name, ns, replicas)` | Scale deployment | Increase/decrease capacity |

## Common Workflows

### 1. Alert Investigation
```
1. alertmanager_get_alerts()              # What's wrong?
2. k8s_get_pod(name, namespace)           # Get pod details
3. k8s_get_events(namespace, pod_name)    # What happened?
4. k8s_get_pod_logs(name, namespace)      # See error logs
5. prometheus_query(...)                  # Check related metrics
```

### 2. Pod Troubleshooting
```
1. k8s_get_pod(name, namespace)           # Current state
2. k8s_get_events(namespace, pod_name)    # Events
3. k8s_get_pod_logs(name, namespace)      # Logs
4. prometheus_query('kube_pod_...')       # Historical metrics
```

### 3. Deployment Issues
```
1. k8s_get_deployment(name, namespace)    # Deployment status
2. k8s_list_pods(namespace, labels)       # List pods
3. k8s_get_pod(name, namespace)           # Check failing pod
4. k8s_restart_deployment(name, ns)       # Remediate
```

### 4. Scaling Decision
```
1. prometheus_query('cpu_usage...')       # Check metrics
2. k8s_get_deployment(name, namespace)    # Current replicas
3. k8s_scale_deployment(name, ns, N)      # Scale
4. prometheus_query('cpu_usage...')       # Verify improvement
```

## Useful PromQL Queries

### Pod Status
```promql
# Pod phase
kube_pod_status_phase{pod="...", namespace="..."}

# Container waiting reason
kube_pod_container_status_waiting_reason{pod="...", namespace="..."}

# Container ready
kube_pod_container_status_ready{pod="...", namespace="..."}
```

### Deployment Status
```promql
# Deployment replicas
kube_deployment_status_replicas{deployment="...", namespace="..."}

# Available replicas
kube_deployment_status_replicas_available{deployment="...", namespace="..."}
```

### Resource Usage
```promql
# CPU usage
rate(container_cpu_usage_seconds_total{pod=~"...*"}[5m]) * 100

# Memory usage
container_memory_working_set_bytes{pod=~"...*"} / 1024 / 1024
```

## Decision Tree

```
Alert Firing?
├─ Yes → Use Prometheus MCP
│   ├─ Get alert details: alertmanager_get_alerts()
│   ├─ Check metrics: prometheus_query(...)
│   └─ Need pod details? → Use Kubernetes MCP
│       ├─ Get pod: k8s_get_pod(...)
│       ├─ Get events: k8s_get_events(...)
│       ├─ Get logs: k8s_get_pod_logs(...)
│       └─ Remediate?
│           ├─ Delete pod: k8s_delete_pod(...)
│           ├─ Restart deployment: k8s_restart_deployment(...)
│           └─ Scale: k8s_scale_deployment(...)
│
└─ No → Proactive monitoring
    ├─ Check services: prometheus_services()
    ├─ Check metrics: prometheus_query(...)
    └─ List pods: k8s_list_pods(...)
```

## Common Patterns

### Pattern: Alert → Diagnose → Fix → Verify
```
1. Prometheus: Get alert
2. Kubernetes: Diagnose (pod, events, logs)
3. Kubernetes: Fix (delete/restart/scale)
4. Prometheus: Verify alert cleared
```

### Pattern: Metrics → Pods → Logs
```
1. Prometheus: High CPU/memory
2. Kubernetes: Find affected pods
3. Kubernetes: Get logs from pods
4. Kubernetes: Remediate
```

### Pattern: Correlation
```
1. Prometheus: Get all alerts
2. For each alert:
   - Kubernetes: Get pod details
   - Kubernetes: Get events
3. Find common root cause
```

## Tips

### When to Use Prometheus MCP
- ✅ Getting alerts
- ✅ Checking metrics and trends
- ✅ Silencing alerts
- ✅ Historical data analysis

### When to Use Kubernetes MCP
- ✅ Getting current pod/deployment state
- ✅ Reading logs
- ✅ Checking events
- ✅ Performing remediation actions

### When to Use Both
- ✅ Complete incident investigation
- ✅ Root cause analysis
- ✅ Remediation with verification
- ✅ Correlation analysis

## Example Commands

### Get all failing pods with metrics
```
1. alertmanager_get_alerts()
2. For each alert with pod label:
   k8s_get_pod(name=alert.labels.pod, namespace=alert.labels.namespace)
```

### Restart all pods in a deployment
```
k8s_restart_deployment(name="my-app", namespace="production")
```

### Scale based on CPU
```
1. prometheus_query('avg(rate(container_cpu_usage_seconds_total{pod=~"my-app.*"}[5m])) * 100')
2. If > 80%: k8s_scale_deployment(name="my-app", namespace="production", replicas=current+2)
```

### Investigate CrashLoopBackOff
```
1. k8s_get_pod(name="...", namespace="...")  # Get state
2. k8s_get_events(namespace="...", pod_name="...")  # Get events
3. k8s_get_pod_logs(name="...", namespace="...", tail_lines=200)  # Get logs
4. prometheus_query('kube_pod_container_status_restarts_total{pod="..."}')  # Restart history
```

