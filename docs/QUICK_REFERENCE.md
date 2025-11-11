# 🚀 MCP Quick Reference - Prompts & Resources

## 📊 Your Resources (3 total)

### 1. Firing Alerts
```
URI: prometheus://alerts/firing
Returns: All currently firing alerts
Usage: "Show me firing alerts"
```

### 2. Specific Metric (Dynamic)
```
URI: prometheus://metrics/{metric_name}
Returns: Data for specified metric
Usage: "Get prometheus://metrics/up"
Example metrics: up, node_cpu_seconds_total, http_requests_total
```

### 3. Dashboard Overview
```
URI: prometheus://dashboard/overview
Returns: CPU, Memory, Disk, Alert counts
Usage: "Show system overview"
```

---

## 🤖 Your Prompts (2 total)

### 1. Alert Analysis
```python
analyze_alert_prompt(alert_name: str, timerange: str = "1h")
```
**What it does:** Fetches alert data + creates AI analysis prompt  
**Returns:** Structured prompt asking AI to analyze root cause, impact, actions, prevention  
**Usage:** "Analyze the 'HighMemoryUsage' alert"

### 2. Performance Analysis
```python
performance_analysis_prompt(service: str, duration: str = "24h")
```
**What it does:** Fetches CPU, memory, requests, errors + creates AI analysis prompt  
**Returns:** Structured prompt asking AI to analyze trends, bottlenecks, capacity, optimization  
**Usage:** "Analyze performance of 'api-service'"

---

## 🎯 When to Use What?

| I want to... | Use this | Example |
|--------------|----------|---------|
| Get raw data | **Resource** | "Show prometheus://dashboard/overview" |
| AI analysis | **Prompt** | "Analyze the 'DiskFull' alert" |
| Execute action | **Tool** | "Silence alert for 2h" |
| Custom query | **Tool** | "Run query 'up{job=\"api\"}'" |

---

## 💬 Example Conversations

### Using Resources
```
You: "What's the current system status?"
AI: [Accesses prometheus://dashboard/overview]
    "CPU: 45%, Memory: 62%, Disk: 78%, Alerts: 2 firing"

You: "Show me all firing alerts"
AI: [Accesses prometheus://alerts/firing]
    "Currently 2 alerts firing: HighMemoryUsage, DiskSpaceLow"

You: "Get the 'up' metric"
AI: [Accesses prometheus://metrics/up]
    "Here are all targets and their up/down status..."
```

### Using Prompts
```
You: "Why is the DatabaseConnectionFailed alert firing?"
AI: [Uses analyze_alert_prompt("DatabaseConnectionFailed")]
    "Based on the alert data:
     
     Root Cause: Connection pool exhausted...
     Impact: 15% of requests failing...
     Actions: 1. Increase pool size, 2. Check for leaks...
     Prevention: Implement connection monitoring..."

You: "Analyze performance of my API service"
AI: [Uses performance_analysis_prompt("api-service")]
    "Performance Analysis:
     
     CPU: Trending up 20% over 24h
     Memory: Stable at 1.2GB
     Requests: 1000 req/s average
     Errors: 0.5% error rate
     
     Bottlenecks: CPU becoming constrained...
     Recommendations: Consider horizontal scaling..."
```

---

## 🧪 Testing Commands

### Test Resources
```bash
# Start server
prometheus-mcp-server

# In another terminal, use MCP Inspector
npx @modelcontextprotocol/inspector prometheus-mcp-server

# Or test programmatically
python examples/demo_prompts_resources.py
```

### Test in VS Code
```
@prometheus show me prometheus://dashboard/overview
@prometheus get prometheus://alerts/firing
@prometheus access prometheus://metrics/up
```

---

## 🔍 Behind the Scenes

### Resource Flow
```
User Request → MCP Client → Resource URI → Your @mcp.resource function
→ Prometheus Query → JSON Response → User
```

### Prompt Flow
```
User Request → MCP Client → Prompt function → Fetch Prometheus data
→ Build structured prompt → Return to AI → AI analyzes → User gets analysis
```

---

## 📝 Code Snippets

### Adding a New Resource
```python
@mcp.resource("prometheus://custom/endpoint")
async def my_custom_resource() -> str:
    """Description of what this provides"""
    result = await prometheus.query('your_promql_query')
    return json.dumps(result, indent=2)
```

### Adding a New Prompt
```python
@mcp.prompt()
async def my_analysis_prompt(param: str) -> str:
    """Description of what this analyzes"""
    data = await prometheus.query(f'query_with_{param}')
    
    return f"""
    Analyze this data:
    
    Data: {json.dumps(data, indent=2)}
    
    Please provide:
    1. Your analysis point 1
    2. Your analysis point 2
    """
```

---

## 🎓 Learning Path

1. ✅ **Read** the full guide: `docs/PROMPTS_AND_RESOURCES_GUIDE.md`
2. ✅ **Run** the demo: `python examples/demo_prompts_resources.py`
3. ✅ **Test** with MCP Inspector
4. ✅ **Try** in VS Code with GitHub Copilot
5. ✅ **Create** your own custom prompts/resources

---

## 🐛 Troubleshooting

**Resource returns error:**
- Check Prometheus is running
- Verify PROMETHEUS_URL is correct
- Test the PromQL query directly in Prometheus UI

**Prompt returns incomplete data:**
- Check if the metric exists in Prometheus
- Verify the query syntax
- Test with a simpler query first

**AI doesn't use prompts/resources:**
- Make sure MCP server is running
- Check VS Code settings.json configuration
- Try explicitly mentioning the resource URI or prompt name

---

## 📚 More Info

- Full Guide: `docs/PROMPTS_AND_RESOURCES_GUIDE.md`
- VS Code Setup: `docs/vscode-integration.md`
- Examples: `examples/README.md`
- MCP Spec: https://spec.modelcontextprotocol.io/

---

**Quick Start:** `python examples/demo_prompts_resources.py` 🚀

