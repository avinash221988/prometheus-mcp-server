# Simple Examples

## 1. Basic Setup

```bash
# Install
pip install -e .

# Set Prometheus URL
export PROMETHEUS_URL=http://localhost:9090

# Start server
prometheus-mcp-server
```

## 2. VS Code Configuration

Add to your `settings.json`:

```json
{
  "github.copilot.chat.tools": {
    "prometheus": {
      "command": "prometheus-mcp-server",
      "env": {
        "PROMETHEUS_URL": "http://localhost:9090"
      }
    }
  }
}
```

## 3. Example Conversations

**Check Service Health:**
```
You: @prometheus are my services healthy?
Copilot: I'll check the status of your services using Prometheus.
[Runs prometheus_services to get 'up' metric results]
```

**Check System Resources:**
```
You: @prometheus how's the CPU looking?
Copilot: Let me check the current CPU usage across your instances.
[Runs prometheus_cpu to get CPU metrics]
```

**Custom Query:**
```
You: @prometheus run query "rate(http_requests_total[5m])"
Copilot: I'll execute that PromQL query for you.
[Runs prometheus_query with your custom query]
```

## 4. Testing Connection

```bash
# Test if Prometheus is reachable
curl http://localhost:9090/-/healthy

# Test MCP server
prometheus-mcp-server --help
```

## 5. Different Prometheus URLs

```bash
# Remote Prometheus
prometheus-mcp-server --prometheus-url https://prometheus.mycompany.com
```
