# Prometheus MCP Server

A **comprehensive** Model Context Protocol (MCP) server that enables AI assistants like GitHub Copilot to interact with Prometheus and Alertmanager for intelligent monitoring and incident response.

## 🚀 What does this do?

This creates an intelligent bridge between AI assistants and your monitoring infrastructure, enabling natural language interactions like:

- *"Are all my services healthy?"*
- *"Show me firing alerts and their impact"*
- *"Analyze the performance of my JFrog platform"*
- *"Silence the disk space alert for 2 hours"*
- *"What's causing high memory usage?"*

## ✨ Features

### 🔧 **Tools** (Direct Actions)
- **prometheus_query** - Execute any PromQL query
- **prometheus_health** - Check Prometheus server health
- **prometheus_cpu** - Get current CPU usage across instances
- **prometheus_memory** - Get current memory usage across instances
- **prometheus_services** - Check service availability (up/down status)
- **alertmanager_silence** - Silence alerts in Alertmanager

### 📊 **Resources** (Live Data Feeds)
- **prometheus://alerts/firing** - Currently firing alerts
- **prometheus://metrics/{metric_name}** - Specific metric data
- **prometheus://dashboard/overview** - System overview (CPU, memory, disk, alerts)

### 🤖 **AI Prompts** (Intelligent Analysis)
- **analyze_alert_prompt** - Generate detailed alert analysis with root cause and remediation
- **performance_analysis_prompt** - Comprehensive service performance analysis

### 🔔 **Alertmanager Integration**
- Create alert silences with duration and reasoning
- Query active/resolved alerts
- Full Alertmanager API support

## 📚 Learning Resources

**New to MCP Prompts & Resources?** Start here:

- 🎓 **[Getting Started Tutorial](docs/GETTING_STARTED_TUTORIAL.md)** - Step-by-step guide for beginners
- 📖 **[Complete Guide](docs/PROMPTS_AND_RESOURCES_GUIDE.md)** - Deep dive into prompts and resources
- 🚀 **[Quick Reference](docs/QUICK_REFERENCE.md)** - Cheat sheet for all features
- 🏗️ **[Architecture](docs/ARCHITECTURE.md)** - How everything works together
- 🧪 **[Interactive Demo](examples/demo_prompts_resources.py)** - Hands-on testing

**Quick Demo:**
```bash
python examples/demo_prompts_resources.py
```

## 🚀 Quick Start

### 1. Install
```bash
# Clone and install
git clone <your-repo-url>
cd prometheus-mcp-server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

### 2. Configure

**Environment Variables:**
```bash
export PROMETHEUS_URL=http://localhost:9090
export ALERTMANAGER_URL=http://localhost:9093  # Optional
export PROMETHEUS_TIMEOUT=30                    # Optional, default: 30
export VERIFY_SSL=true                          # Optional, default: true
```

**Command-Line Arguments:**
```bash
prometheus-mcp-server \
  --prometheus-url https://prometheus.example.com \
  --alertmanager-url https://alertmanager.example.com \
  --timeout 60 \
  --no-verify-ssl  # For self-signed certificates
```

### 3. Test Connection
```bash
# Start the server
prometheus-mcp-server

# Should show: "Starting Prometheus MCP Server (connecting to http://localhost:9090)"
```

### 4. VS Code Integration

Add to your VS Code `settings.json`:

```json
{
  "github.copilot.chat.tools": {
    "prometheus": {
      "command": "/path/to/your/venv/bin/python",
      "args": [
        "-m", "prometheus_mcp_server.simple_server",
        "--prometheus-url", "http://localhost:9090"
      ],
      "cwd": "/path/to/prometheus-mcp-server",
      "description": "Query Prometheus metrics and monitoring data"
    }
  }
}
```

## 💬 Usage Examples

### Basic Monitoring
```
@prometheus are all services healthy?
@prometheus what's the current CPU usage?
@prometheus show me memory usage trends
```

### Alert Management
```
@prometheus what alerts are currently firing?
@prometheus silence the "DiskSpaceHigh" alert for 2 hours because "planned maintenance"
@prometheus analyze the "DatabaseConnectionFailed" alert
```

### Performance Analysis
```
@prometheus analyze performance of "jfrog-platform" service
@prometheus show me container memory usage in namespace "prod"
@prometheus what's the error rate for my APIs?
```

### Advanced Queries
```
@prometheus run query "rate(http_requests_total[5m])"
@prometheus run query "container_memory_working_set_bytes{namespace='prod'}"
```

## 🔧 Configuration Options

| Option | Environment Variable | Command-Line Flag | Default |
|--------|---------------------|-------------------|---------|
| Prometheus URL | `PROMETHEUS_URL` | `--prometheus-url` | `http://localhost:9090` |
| Alertmanager URL | `ALERTMANAGER_URL` | `--alertmanager-url` | `http://localhost:9093` |
| Timeout | `PROMETHEUS_TIMEOUT` | `--timeout` | `30` |
| SSL Verification | `VERIFY_SSL` | `--no-verify-ssl` | `true` |

## 📋 Complete Tool Reference

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| `prometheus_query` | Execute custom PromQL | `prometheus_query("up{job='kubernetes-nodes'}")` |
| `prometheus_health` | Server health check | Always returns current status |
| `prometheus_cpu` | System CPU usage | Aggregated across all monitored instances |
| `prometheus_memory` | System memory usage | Aggregated memory utilization |
| `prometheus_services` | Service availability | Shows up/down status via 'up' metric |
| `alertmanager_silence` | Silence alerts | `alertmanager_silence("DiskHigh", "2h", "maintenance")` |

## 🎯 Resource Access

Resources provide live data that AI can reference:

- **View firing alerts**: The AI can automatically check `prometheus://alerts/firing`
- **System overview**: Get dashboard data from `prometheus://dashboard/overview`
- **Specific metrics**: Access any metric via `prometheus://metrics/{name}`

## 🤖 AI-Powered Analysis

The server includes intelligent prompts that help AI provide deeper insights:

- **Alert Analysis**: Automatically generates root cause analysis, impact assessment, and remediation steps
- **Performance Analysis**: Provides comprehensive service performance reports with optimization recommendations

## 🛠 Troubleshooting

### Connection Issues
```bash
# Test Prometheus connectivity
curl http://localhost:9090/-/healthy

# Test with authentication
curl -H "Authorization: Bearer $TOKEN" https://your-prometheus/-/healthy
```

### VS Code Integration Issues
1. **Restart VS Code** after updating settings
2. **Check paths** in settings.json are absolute
3. **Verify environment variables** are set correctly
4. **Test MCP server** independently first

### Common Problems

**Server won't start?**
- Verify Prometheus URL is accessible
- Check network connectivity and firewall rules
- Ensure authentication credentials are correct

**AI can't access tools?**
- Confirm VS Code settings.json syntax is valid
- Restart VS Code after configuration changes
- Check MCP server logs for connection errors

**Queries timeout?**
- Increase `PROMETHEUS_TIMEOUT` value
- Optimize PromQL queries for better performance
- Check Prometheus server performance

## 🔮 What's Next?

Enhance your monitoring setup:

- **Custom Dashboards**: Use resources to create dynamic monitoring views
- **Automated Runbooks**: Combine prompts with tools for intelligent incident response
- **Multi-Cluster**: Connect multiple Prometheus instances for centralized monitoring
- **Custom Metrics**: Add domain-specific monitoring tools for your applications

## 📄 Example Configurations

### Production Setup
```json
{
  "github.copilot.chat.tools": {
    "prometheus": {
      "command": "/usr/local/bin/python",
      "args": [
        "-m", "prometheus_mcp_server.simple_server",
        "--prometheus-url", "https://prometheus.prod.company.com"
      ],
      "env": {
        "PROMETHEUS_AUTH_TOKEN": "${PROMETHEUS_TOKEN}",
        "ALERTMANAGER_URL": "https://alertmanager.prod.company.com",
        "PROMETHEUS_TIMEOUT": "60"
      },
      "description": "Production monitoring assistant"
    }
  }
}
```

Start building intelligent monitoring workflows today! 🚀