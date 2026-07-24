# Setup Guide

## Prerequisites

- Python 3.9+
- A running Prometheus instance
- (Optional) A running Alertmanager instance
- A valid `kubeconfig` for Kubernetes access

---

## Installation

```bash
git clone https://github.com/avinash221988/prometheus-mcp-server.git
cd prometheus-mcp-server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

---

## Prometheus MCP Server

### Configuration

| Option | Env Variable | CLI Flag | Default |
|--------|-------------|----------|---------|
| Prometheus URL | `PROMETHEUS_URL` | `--prometheus-url` | `http://localhost:9090` |
| Alertmanager URL | `ALERTMANAGER_URL` | `--alertmanager-url` | `http://localhost:9093` |
| Timeout | `PROMETHEUS_TIMEOUT` | `--timeout` | `30` |
| SSL Verification | `VERIFY_SSL` | `--no-verify-ssl` | `true` |

### Start

```bash
prometheus-mcp-server \
  --prometheus-url https://prometheus.example.com \
  --alertmanager-url https://alertmanager.example.com \
  --timeout 60 \
  --no-verify-ssl
```

---

## Kubernetes MCP Server

### Configuration

| Option | Env Variable | Default |
|--------|-------------|---------|
| Kubernetes context | `K8S_CONTEXT` | current kubeconfig context |
| Default namespace | `K8S_NAMESPACE` | `default` |

### Start

```bash
k8s-mcp-server
# Or with a specific context:
K8S_CONTEXT=my-cluster k8s-mcp-server
```

---

## Augment (Auggie) Integration

```bash
# Add Prometheus MCP server
auggie mcp add prometheus-server -- /path/to/venv/bin/python \
  -m prometheus_mcp_server.simple_server \
  --prometheus-url https://your-prometheus-url \
  --alertmanager-url https://your-alertmanager-url \
  --timeout 30 --no-verify-ssl

# Add Kubernetes MCP server
auggie mcp add k8s-server -- /path/to/venv/bin/k8s-mcp-server

# Verify
auggie mcp list
```

---

## VS Code (GitHub Copilot) Integration

Add to `settings.json`:

```json
{
  "github.copilot.chat.tools": {
    "prometheus": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "prometheus_mcp_server.simple_server", "--prometheus-url", "http://localhost:9090"],
      "description": "Prometheus and Alertmanager monitoring"
    }
  }
}
```

> Restart VS Code after updating settings. Ensure all paths are absolute.

---

## Troubleshooting

**Prometheus unreachable**
```bash
curl http://localhost:9090/-/healthy
```

**K8s `describe_pod` fails with `pod_ips` error**
Known bug in `k8s_describe_pod` — `pod.status.pod_ips` may be `None` for pods that never started. Use `k8s_get_events` and `k8s_get_pod_status` as alternatives.

**Queries timeout** — Increase `PROMETHEUS_TIMEOUT` or optimise your PromQL.

**Image pull errors in K8s** — Check ECR/registry credentials and verify the image tag exists.
