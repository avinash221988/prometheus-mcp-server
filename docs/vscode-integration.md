# VS Code + GitHub Copilot Integration

Complete guide for integrating the enhanced Prometheus MCP server with **GitHub Copilot in VS Code** for intelligent monitoring workflows.

## � Quick Setup

### GitHub Copilot Chat Integration (Recommended)

Add to your VS Code **workspace settings** (`.vscode/settings.json`):

```json
{
  "github.copilot.chat.tools": {
    "prometheus": {
      "command": "/path/to/your/venv/bin/python",
      "args": [
        "-m", "prometheus_mcp_server.simple_server",
        "--prometheus-url", "https://your-prometheus-server.com"
      ],
      "cwd": "/path/to/prometheus-mcp-server",
      "env": {
        "PROMETHEUS_URL": "https://your-prometheus-server.com",
        "ALERTMANAGER_URL": "https://your-alertmanager-server.com",
        "PROMETHEUS_TIMEOUT": "30"
      },
      "description": "Intelligent Prometheus monitoring and alerting assistant"
    }
  }
}
```

## 🔧 Configuration Examples

### Basic Local Setup
```json
{
  "github.copilot.chat.tools": {
    "prometheus": {
      "command": "/Users/yourname/prometheus-mcp-server/venv/bin/python",
      "args": [
        "-m", "prometheus_mcp_server.simple_server",
        "--prometheus-url", "http://localhost:9090"
      ],
      "cwd": "/Users/yourname/prometheus-mcp-server",
      "description": "Local Prometheus monitoring"
    }
  }
}
```

### Production Setup with Authentication
```json
{
  "github.copilot.chat.tools": {
    "prometheus": {
      "command": "/usr/local/bin/python",
      "args": [
        "-m", "prometheus_mcp_server.simple_server"
      ],
      "env": {
        "PROMETHEUS_URL": "https://prometheus.prod.company.com",
        "ALERTMANAGER_URL": "https://alertmanager.prod.company.com", 
        "PROMETHEUS_AUTH_TOKEN": "${PROMETHEUS_TOKEN}",
        "PROMETHEUS_TIMEOUT": "60"
      },
      "description": "Production monitoring assistant with alerting"
    }
  }
}
```

### Multi-Environment Setup
```json
{
  "github.copilot.chat.tools": {
    "prometheus-prod": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "prometheus_mcp_server.simple_server"],
      "env": {
        "PROMETHEUS_URL": "https://prometheus-prod.company.com",
        "ALERTMANAGER_URL": "https://alertmanager-prod.company.com"
      },
      "description": "Production monitoring"
    },
    "prometheus-staging": {
      "command": "/path/to/venv/bin/python", 
      "args": ["-m", "prometheus_mcp_server.simple_server"],
      "env": {
        "PROMETHEUS_URL": "https://prometheus-staging.company.com"
      },
      "description": "Staging environment monitoring"
    }
   }
}
```

## 💬 Enhanced Usage Examples

Once configured, you can leverage all the enhanced MCP features through GitHub Copilot Chat:

### 🔧 **Using Tools (Direct Actions)**
```
@prometheus check if all services are healthy
@prometheus what's the current CPU and memory usage?
@prometheus run query "rate(http_requests_total[5m])"
@prometheus silence the "DiskSpaceHigh" alert for 2 hours because "planned maintenance"
```

### 📊 **Accessing Resources (Live Data)**
```
@prometheus show me the current system overview
@prometheus what alerts are currently firing?
@prometheus get data for the "up" metric
```

### 🤖 **Using AI Prompts (Intelligent Analysis)**
```
@prometheus analyze the "DatabaseConnectionFailed" alert
@prometheus analyze performance of the "jfrog-platform" service over the last 24 hours
```

### 🔔 **Alert Management**
```
@prometheus list all firing alerts
@prometheus silence alert "HighMemoryUsage" for "4h" with reason "investigating memory leak"
@prometheus what's the impact of the current alerts?
```## 🚀 VS Code Tasks Integration

Add Prometheus MCP server as a VS Code task (`.vscode/tasks.json`):

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start Enhanced Prometheus MCP Server",
            "type": "shell",
            "command": "${workspaceFolder}/venv/bin/python",
            "args": [
                "-m", "prometheus_mcp_server.simple_server",
                "--prometheus-url", "http://localhost:9090"
            ],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "isBackground": true,
            "problemMatcher": []
        }
    ]
}
```

## 🔌 Custom Copilot Integration Script

Create a Python script for direct integration:

```python
# copilot_prometheus.py
"""
GitHub Copilot integration script for Prometheus MCP server.
Use this to enable Prometheus queries directly from Copilot.
"""

import asyncio
import json
import sys
from prometheus_mcp_server import Config, PrometheusClient

async def copilot_query(query_type: str, **kwargs):
    """Execute Prometheus query for Copilot."""
    config = Config.load_from_env()
    
    async with PrometheusClient(config) as client:
        if query_type == "instant":
            result = await client.instant_query(kwargs["query"])
        elif query_type == "range":
            result = await client.range_query(
                kwargs["query"],
                kwargs["start"], 
                kwargs["end"],
                kwargs["step"]
            )
        elif query_type == "health":
            result = await client.health_check()
        elif query_type == "metrics":
            result = {"metrics": await client.get_metrics_list()}
        else:
            result = {"error": f"Unknown query type: {query_type}"}
    
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python copilot_prometheus.py <query_type> [args...]")
        sys.exit(1)
    
    query_type = sys.argv[1]
    # Parse additional arguments as needed
    result = asyncio.run(copilot_query(query_type, query="up"))
    print(result)
```

## 🛠️ Development Workflow with VS Code

### 1. Integrated Terminal Usage
```bash
# Start MCP server in VS Code terminal
Ctrl+` (open terminal)
prometheus-mcp-server --prometheus-url http://localhost:9090

# Or use the VS Code task
Ctrl+Shift+P → "Tasks: Run Task" → "Start Prometheus MCP Server"
```

### 2. Debugging Configuration
**`.vscode/launch.json`:**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Prometheus MCP Server",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/prometheus_mcp_server/cli.py",
            "args": [
                "--prometheus-url", "http://localhost:9090",
                "--log-level", "DEBUG"
            ],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        }
    ]
}
```

### 3. Copilot Chat Custom Instructions

Add this to your workspace for better Copilot integration:

**`.vscode/copilot-instructions.md`:**
```markdown
# Prometheus MCP Server Instructions for Copilot

When the user asks about monitoring, metrics, or Prometheus:

1. Use the prometheus-mcp-server tools available in this workspace
2. For current values, use instant queries
3. For trends over time, use range queries  
4. Always check health status first if there are connection issues
5. Suggest relevant PromQL queries based on the user's needs

Available tools:
- prometheus_instant_query: Get current metric values
- prometheus_range_query: Get time-series data
- prometheus_health_check: Check server health
- prometheus_list_metrics: Discover available metrics
- prometheus_metric_metadata: Get metric details
- prometheus_get_targets: Check scrape targets

Example queries:
- Current CPU: `up`
- Memory usage: `node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes`
- HTTP requests: `rate(http_requests_total[5m])`
```

## 🔄 Automation Scripts

### Auto-start Script
```bash
#!/bin/bash
# start_prometheus_mcp.sh

echo "Starting Prometheus MCP Server for VS Code..."

# Check if Prometheus is running
if ! curl -s http://localhost:9090/-/healthy > /dev/null; then
    echo "Warning: Prometheus server not reachable at http://localhost:9090"
fi

# Start MCP server
prometheus-mcp-server \
    --prometheus-url http://localhost:9090 \
    --log-level INFO

echo "Prometheus MCP Server started successfully!"
```

### Health Check Script
```python
#!/usr/bin/env python3
# health_check.py

"""Quick health check script for VS Code integration."""

import asyncio
from prometheus_mcp_server import Config, PrometheusClient

async def main():
    config = Config.load_from_env()
    print(f"Checking Prometheus at {config.prometheus_url}...")
    
    try:
        async with PrometheusClient(config) as client:
            health = await client.health_check()
            print("✅ Prometheus MCP Server: HEALTHY")
            print(f"   Response time: {health.get('response_time_ms', 0):.2f}ms")
        return True
    except Exception as e:
        print(f"❌ Prometheus MCP Server: FAILED - {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
```

## 📋 Quick Setup Checklist

- [ ] Install Python dependencies: `pip install -e .`
- [ ] Configure Prometheus URL in `.env` file
- [ ] Test connection: `python health_check.py`
- [ ] Add VS Code MCP configuration to `settings.json`
- [ ] Enable GitHub Copilot MCP integration
- [ ] Test with Copilot Chat: `@prometheus check health`
- [ ] Add VS Code tasks for easy server management

## 🎯 Pro Tips for VS Code + Copilot

1. **Use Workspace Settings**: Store MCP config in `.vscode/settings.json` for team sharing
2. **Create Shortcuts**: Add keybindings for common Prometheus queries
3. **Integrate with Tasks**: Use VS Code tasks to manage the MCP server lifecycle
4. **Custom Snippets**: Create Prometheus query snippets for faster development
5. **Extension Development**: Consider building a dedicated VS Code extension for your team

## 🐛 Troubleshooting VS Code Integration

**MCP Server Not Found:**
```bash
# Check if server is in PATH
which prometheus-mcp-server

# Or use absolute path in VS Code config
"/path/to/venv/bin/prometheus-mcp-server"
```

**Copilot Not Using Tools:**
```json
// Ensure MCP is enabled in VS Code settings
{
  "github.copilot.advanced": {
    "mcp.enabled": true
  }
}
```

**Connection Issues:**
```bash
# Test manually first
prometheus-mcp-server --prometheus-url http://localhost:9090 --log-level DEBUG
```

This setup gives you the power of Prometheus monitoring directly within your VS Code + GitHub Copilot workflow! 🚀