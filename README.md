# Prometheus & Kubernetes MCP Server

MCP servers that enable AI assistants (Augment, GitHub Copilot) to interact with **Prometheus**, **Alertmanager**, and **Kubernetes** using natural language.

> 📖 For installation, configuration, and integration details see **[docs/SETUP.md](docs/SETUP.md)**

---

## MCP Servers

### 🔥 Prometheus MCP Server (`prometheus-mcp-server`)

| Tool | Description |
|------|-------------|
| `prometheus_query` | Execute any PromQL query |
| `prometheus_health` | Check Prometheus server health |
| `prometheus_cpu` | CPU usage across all instances |
| `prometheus_memory` | Memory usage across all instances |
| `prometheus_services` | Service up/down status |
| `alertmanager_get_alerts` | List active/all alerts |
| `alertmanager_silence` | Silence an alert (name, duration, reason) |
| `alertmanager_get_silences` | List all silences |
| `alertmanager_delete_silence` | Expire a silence by ID |

**Resources:** `prometheus://alerts/firing` · `prometheus://metrics/{name}` · `prometheus://dashboard/overview`

---

### ☸️ Kubernetes MCP Server (`k8s-mcp-server`)

| Tool | Description | Status |
|------|-------------|--------|
| `k8s_get_pod_status` | Pod status summary for a namespace | ✅ Working |
| `k8s_get_events` | Recent events in a namespace | ✅ Working |
| `k8s_get_pod_logs` | Tail logs from a pod | ✅ Working (fails if container never started) |
| `k8s_scale_deployment` | Scale a deployment to N replicas | ✅ Working |
| `k8s_restart_deployment` | Rollout restart a deployment | ✅ Working |
| `k8s_describe_pod` | Detailed pod description | ⚠️ Known bug — see below |

**Resources:** `k8s://pods` · `k8s://deployments` · `k8s://services` · `k8s://nodes` · `k8s://namespaces`

#### ⚠️ Known Issue — `k8s_describe_pod`
Fails with `'V1PodStatus' object has no attribute 'pod_ips'` when `pod.status.pod_ips` is `None` (e.g. pods stuck in Pending/Failed before ever getting an IP). Use `k8s_get_events` and `k8s_get_pod_status` as effective alternatives for troubleshooting.

---

## Example Interactions

```
# Prometheus / Alertmanager
"What alerts are currently firing?"
"Silence the DiskSpaceHigh alert for 2 hours — planned maintenance"
"Run query rate(http_requests_total[5m])"

# Kubernetes
"Show pod status in namespace registry-adapter-stubbed-showcase"
"Get recent events for namespace argocd"
"Restart the registry-adapter deployment"
"Scale registry-adapter to 3 replicas"
```

---

## Quick Start

```bash
git clone https://github.com/avinash221988/prometheus-mcp-server.git
cd prometheus-mcp-server
pip install -e .
```

See **[docs/SETUP.md](docs/SETUP.md)** for full configuration and integration steps.