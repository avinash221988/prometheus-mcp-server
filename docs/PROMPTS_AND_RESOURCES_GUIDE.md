# 🎓 MCP Prompts and Resources - Complete Guide

## 📚 Understanding MCP Concepts

### What is MCP (Model Context Protocol)?

MCP is a protocol that allows AI assistants to interact with external systems through three main primitives:

1. **🔧 Tools** - Direct actions the AI can execute (like functions)
2. **📊 Resources** - Live data sources the AI can read from (like APIs)
3. **🤖 Prompts** - Pre-built prompt templates for common analysis tasks

---

## 🎯 Your Implementation Overview

Your Prometheus MCP server has:

### ✅ **3 Resources** (Data Sources)
- `prometheus://alerts/firing` - Currently firing alerts
- `prometheus://metrics/{metric_name}` - Specific metric data
- `prometheus://dashboard/overview` - System overview dashboard

### ✅ **2 Prompts** (AI Analysis Templates)
- `analyze_alert_prompt` - Detailed alert analysis
- `performance_analysis_prompt` - Service performance analysis

### ✅ **6 Tools** (Actions)
- `prometheus_query` - Execute custom PromQL
- `prometheus_health` - Health check
- `prometheus_cpu` - CPU metrics
- `prometheus_memory` - Memory metrics
- `prometheus_services` - Service status
- `alertmanager_silence` - Silence alerts

---

## 📊 RESOURCES - Live Data Sources

### What are Resources?

Resources are **read-only data sources** that provide live information. Think of them as REST API endpoints that the AI can access to get current state.

### Your Resources Explained

#### 1️⃣ **Firing Alerts Resource**
```
URI: prometheus://alerts/firing
```

**What it does:** Returns all currently firing alerts from Prometheus

**Code:**
```python
@mcp.resource("prometheus://alerts/firing")
async def get_firing_alerts() -> str:
    result = await prometheus.query('ALERTS{alertstate="firing"}')
    return json.dumps(result, indent=2)
```

**How to use in AI chat:**
```
"Show me all firing alerts"
"What alerts are currently active?"
"Access the prometheus://alerts/firing resource"
```

---

#### 2️⃣ **Metric Resource (Dynamic)**
```
URI: prometheus://metrics/{metric_name}
```

**What it does:** Returns data for any specific metric (dynamic parameter)

**Code:**
```python
@mcp.resource("prometheus://metrics/{metric_name}")
async def get_metric(metric_name: str) -> str:
    result = await prometheus.query(metric_name)
    return json.dumps(result, indent=2)
```

**How to use in AI chat:**
```
"Get the 'up' metric from prometheus://metrics/up"
"Show me prometheus://metrics/node_cpu_seconds_total"
"Access resource prometheus://metrics/http_requests_total"
```

---

#### 3️⃣ **Dashboard Overview Resource**
```
URI: prometheus://dashboard/overview
```

**What it does:** Provides a comprehensive system overview (CPU, memory, disk, alerts)

**Code:**
```python
@mcp.resource("prometheus://dashboard/overview")
async def get_dashboard_overview() -> str:
    queries = {
        "cpu": "avg(100 - (avg by(instance) (irate(...))))",
        "memory": "avg((1 - (node_memory_MemAvailable_bytes / ...)))",
        "disk": "avg(100 - ((node_filesystem_avail_bytes / ...)))",
        "alerts": "count(ALERTS{alertstate='firing'})"
    }
    # Executes all queries and returns combined results
```

**How to use in AI chat:**
```
"Show me the system overview"
"Access prometheus://dashboard/overview"
"What's the current state of all systems?"
```

---

## 🤖 PROMPTS - AI Analysis Templates

### What are Prompts?

Prompts are **pre-built templates** that structure how the AI should analyze data. They fetch relevant data and provide it to the AI with specific analysis instructions.

### Your Prompts Explained

#### 1️⃣ **Alert Analysis Prompt**

**Function signature:**
```python
@mcp.prompt()
async def analyze_alert_prompt(alert_name: str, timerange: str = "1h") -> str
```

**What it does:**
1. Fetches data for the specified alert
2. Creates a structured prompt asking the AI to analyze:
   - Root cause
   - Impact assessment
   - Recommended actions
   - Prevention strategies

**How to use in AI chat:**
```
"Analyze the 'HighMemoryUsage' alert"
"Use analyze_alert_prompt for 'DatabaseConnectionFailed'"
"Investigate the 'DiskSpaceLow' alert over the last 2h"
```

**What happens behind the scenes:**
```python
# 1. Fetches alert data
alert_data = await prometheus.query(f'ALERTS{{alertname="{alert_name}"}}')

# 2. Returns structured prompt
return f"""
Analyze this Prometheus alert:

Alert: {alert_name}
Time Range: {timerange}
Data: {json.dumps(alert_data, indent=2)}

Please provide:
1. Root cause analysis
2. Impact assessment
3. Recommended actions
4. Prevention strategies
"""
```

---

#### 2️⃣ **Performance Analysis Prompt**

**Function signature:**
```python
@mcp.prompt()
async def performance_analysis_prompt(service: str, duration: str = "24h") -> str
```

**What it does:**
1. Fetches multiple performance metrics for a service:
   - CPU usage
   - Memory usage
   - Request rate
   - Error rate
2. Creates a structured prompt asking the AI to analyze:
   - Performance trends
   - Bottlenecks
   - Capacity planning
   - Optimization opportunities

**How to use in AI chat:**
```
"Analyze performance of 'api-service'"
"Use performance_analysis_prompt for 'jfrog-platform' over 48h"
"Check performance trends for 'database-service'"
```

**What happens behind the scenes:**
```python
# 1. Fetches multiple metrics
queries = {
    "cpu": f'avg(rate(container_cpu_usage_seconds_total{{pod=~"{service}.*"}}[5m])) * 100',
    "memory": f'avg(container_memory_working_set_bytes{{pod=~"{service}.*"}}) / 1024 / 1024',
    "requests": f'sum(rate(http_requests_total{{service="{service}"}}[5m]))',
    "errors": f'sum(rate(http_requests_total{{service="{service}",status=~"5.."}}[5m]))'
}

# 2. Returns structured analysis prompt with all metrics
```

---

## 🧪 Testing Your Implementation

### Step 1: Start Your MCP Server

```bash
# Make sure Prometheus is running
export PROMETHEUS_URL=http://localhost:9090

# Start the server
prometheus-mcp-server
```

### Step 2: Test with MCP Inspector

```bash
# Install MCP Inspector (if not already installed)
npm install -g @modelcontextprotocol/inspector

# Run inspector
mcp-inspector prometheus-mcp-server
```

This opens a web UI where you can:
- See all available resources, prompts, and tools
- Test each one interactively
- View the actual responses

### Step 3: Test in VS Code with GitHub Copilot

Add to your `.vscode/settings.json`:
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

Then in Copilot Chat:
```
@prometheus show me prometheus://dashboard/overview
@prometheus analyze the 'HighCPU' alert
@prometheus analyze performance of 'my-service'
```

---

## 💡 Practical Examples

### Example 1: Using Resources for Quick Status Check

**User:** "What's the current system status?"

**AI uses:** `prometheus://dashboard/overview` resource

**Result:** Gets CPU, memory, disk, and alert counts in one call

---

### Example 2: Using Prompts for Deep Analysis

**User:** "Why is the DatabaseConnectionFailed alert firing?"

**AI uses:** `analyze_alert_prompt("DatabaseConnectionFailed")`

**Result:** 
- Fetches alert data
- AI analyzes root cause
- Provides remediation steps
- Suggests prevention strategies

---

### Example 3: Combining Resources and Prompts

**User:** "Analyze the performance issues with my API service"

**AI workflow:**
1. Uses `prometheus://dashboard/overview` to get overall health
2. Uses `performance_analysis_prompt("api-service")` for detailed analysis
3. May use `prometheus://alerts/firing` to check related alerts
4. Provides comprehensive analysis with data-driven recommendations

---

## 🔍 Key Differences

| Feature | Resources | Prompts | Tools |
|---------|-----------|---------|-------|
| **Purpose** | Provide data | Structure AI analysis | Execute actions |
| **Direction** | Read-only | Read + AI instruction | Read/Write |
| **When to use** | Need current state | Need AI analysis | Need to change something |
| **Example** | Get firing alerts | Analyze an alert | Silence an alert |

---

## 🎯 Best Practices

### For Resources:
✅ Use for frequently accessed data  
✅ Keep responses JSON formatted  
✅ Use URI patterns for dynamic data  
✅ Cache when appropriate  

### For Prompts:
✅ Fetch all relevant data upfront  
✅ Provide clear analysis instructions  
✅ Include context (timeranges, parameters)  
✅ Structure output expectations  

---

## 🚀 Next Steps

1. **Test each resource** using MCP Inspector
2. **Try the prompts** with different alert names and services
3. **Monitor the logs** to see what data is being fetched
4. **Experiment** with combining resources and prompts in AI conversations

---

## 📖 Additional Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Prometheus Query Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)

---

**Happy Learning! 🎉**

