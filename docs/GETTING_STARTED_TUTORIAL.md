# 🎓 Getting Started Tutorial - MCP Prompts & Resources

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ Python 3.8+ installed
- ✅ Prometheus running (or access to a Prometheus server)
- ✅ Your MCP server installed (`pip install -e .`)

---

## 🚀 Step 1: Verify Your Setup

### 1.1 Check Prometheus Connection

```bash
# Set your Prometheus URL
export PROMETHEUS_URL=http://localhost:9090

# Test connection
curl $PROMETHEUS_URL/api/v1/query?query=up
```

You should see JSON response with metrics data.

### 1.2 Verify MCP Server Installation

```bash
# Check if command is available
which prometheus-mcp-server

# Or try running it
prometheus-mcp-server --help
```

---

## 🧪 Step 2: Run the Interactive Demo

This is the **best way to learn** - it shows you exactly how prompts and resources work!

```bash
# Navigate to your project directory
cd /path/to/prometheus-mcp-server

# Run the demo
python examples/demo_prompts_resources.py
```

### What You'll See:

```
🚀 MCP PROMPTS & RESOURCES DEMONSTRATION

Prometheus URL: http://localhost:9090

Checking Prometheus connection...
✅ Prometheus is healthy and reachable!

Choose a demo:
  1. Test all Resources (data sources)
  2. Test all Prompts (AI templates)
  3. Compare Resources vs Prompts
  4. Run all demos
  5. Exit

Enter choice (1-5):
```

### Try Each Option:

**Option 1: Test Resources**
- See how each resource fetches data
- Understand what data each resource provides
- Learn the URI patterns

**Option 2: Test Prompts**
- See how prompts fetch data AND create instructions
- Understand the structure of AI analysis prompts
- Learn when to use prompts vs resources

**Option 3: Compare**
- See the key differences side-by-side
- Understand when to use each approach

---

## 🔍 Step 3: Understand What You Have

### Your Resources (3 total)

Open `src/prometheus_mcp_server/simple_server.py` and look at lines 53-83:

<augment_code_snippet path="src/prometheus_mcp_server/simple_server.py" mode="EXCERPT">
````python
@mcp.resource("prometheus://alerts/firing")
async def get_firing_alerts() -> str:
    """Resource for currently firing alerts."""
    result = await prometheus.query('ALERTS{alertstate="firing"}')
    return json.dumps(result, indent=2)
````
</augment_code_snippet>

**Key Points:**
- `@mcp.resource()` decorator registers it as a resource
- URI pattern: `prometheus://alerts/firing`
- Returns JSON string
- Read-only data access

### Your Prompts (2 total)

Look at lines 85-132:

<augment_code_snippet path="src/prometheus_mcp_server/simple_server.py" mode="EXCERPT">
````python
@mcp.prompt()
async def analyze_alert_prompt(alert_name: str, timerange: str = "1h") -> str:
    """Generate analysis prompt for a specific alert."""
    alert_data = await prometheus.query(f'ALERTS{{alertname="{alert_name}"}}')
    
    return f"""
    Analyze this Prometheus alert:
    ...
````
</augment_code_snippet>

**Key Points:**
- `@mcp.prompt()` decorator registers it as a prompt
- Takes parameters (alert_name, timerange)
- Fetches data from Prometheus
- Returns formatted prompt with instructions

---

## 🎯 Step 4: Test with MCP Inspector

MCP Inspector is a web UI for testing MCP servers.

### 4.1 Install MCP Inspector

```bash
npm install -g @modelcontextprotocol/inspector
```

### 4.2 Run Inspector

```bash
# Make sure Prometheus URL is set
export PROMETHEUS_URL=http://localhost:9090

# Start inspector
npx @modelcontextprotocol/inspector prometheus-mcp-server
```

This opens a web browser with an interactive UI.

### 4.3 Test Resources

1. Click on **"Resources"** tab
2. You'll see:
   - `prometheus://alerts/firing`
   - `prometheus://metrics/{metric_name}`
   - `prometheus://dashboard/overview`
3. Click on any resource to see its data
4. For dynamic resources, enter parameters (e.g., `up` for metric_name)

### 4.4 Test Prompts

1. Click on **"Prompts"** tab
2. You'll see:
   - `analyze_alert_prompt`
   - `performance_analysis_prompt`
3. Click on a prompt
4. Enter parameters (e.g., alert_name: "HighMemoryUsage")
5. See the generated prompt with data and instructions

---

## 💬 Step 5: Use with AI Assistant (VS Code)

### 5.1 Configure VS Code

Add to `.vscode/settings.json`:

```json
{
  "github.copilot.chat.tools": {
    "prometheus": {
      "command": "prometheus-mcp-server",
      "env": {
        "PROMETHEUS_URL": "http://localhost:9090"
      },
      "description": "Prometheus monitoring assistant"
    }
  }
}
```

### 5.2 Test Resources in Chat

Open GitHub Copilot Chat and try:

```
@prometheus show me prometheus://dashboard/overview
```

```
@prometheus get prometheus://alerts/firing
```

```
@prometheus access prometheus://metrics/up
```

### 5.3 Test Prompts in Chat

```
@prometheus analyze the "HighMemoryUsage" alert
```

```
@prometheus analyze performance of "api-service" over 24h
```

---

## 🎨 Step 6: Create Your Own Resource

Let's add a new resource for top CPU consumers!

### 6.1 Add the Code

Open `src/prometheus_mcp_server/simple_server.py` and add after line 83:

```python
@mcp.resource("prometheus://top/cpu")
async def get_top_cpu_consumers() -> str:
    """Resource for top CPU consuming processes."""
    query = 'topk(5, rate(process_cpu_seconds_total[5m]))'
    result = await prometheus.query(query)
    return json.dumps(result, indent=2)
```

### 6.2 Test It

```bash
# Restart your MCP server
prometheus-mcp-server
```

In another terminal:
```bash
# Test with inspector
npx @modelcontextprotocol/inspector prometheus-mcp-server
```

Look for your new resource: `prometheus://top/cpu`

### 6.3 Use It

In VS Code Copilot Chat:
```
@prometheus show me prometheus://top/cpu
```

---

## 🤖 Step 7: Create Your Own Prompt

Let's add a capacity planning prompt!

### 7.1 Add the Code

Add to `simple_server.py`:

```python
@mcp.prompt()
async def capacity_planning_prompt(resource_type: str = "cpu", days: str = "7") -> str:
    """Generate capacity planning analysis prompt."""
    
    # Fetch historical data
    if resource_type == "cpu":
        query = f'avg_over_time(node_cpu_usage[{days}d])'
    elif resource_type == "memory":
        query = f'avg_over_time(node_memory_usage[{days}d])'
    else:
        query = f'avg_over_time(node_{resource_type}_usage[{days}d])'
    
    try:
        data = await prometheus.query(query)
    except Exception as e:
        data = {"error": str(e)}
    
    return f"""
    Capacity Planning Analysis for {resource_type}:
    
    Historical Data ({days} days): {json.dumps(data, indent=2)}
    
    Please analyze:
    1. Current utilization trends
    2. Growth rate
    3. Projected capacity needs (30/60/90 days)
    4. Scaling recommendations
    5. Cost implications
    """
```

### 7.2 Test It

```bash
# Restart server
prometheus-mcp-server
```

In Copilot Chat:
```
@prometheus create capacity plan for CPU over 7 days
```

---

## 📊 Step 8: Understanding the Differences

### When to Use Resources:

✅ You need raw data  
✅ You want to display current state  
✅ You're building a dashboard  
✅ You need specific metric values  

**Example:** "Show me all firing alerts"

### When to Use Prompts:

✅ You need AI analysis  
✅ You want recommendations  
✅ You need root cause analysis  
✅ You want structured insights  

**Example:** "Why is this alert firing and what should I do?"

### When to Use Tools:

✅ You need to execute an action  
✅ You want to change state  
✅ You need custom query execution  

**Example:** "Silence this alert for 2 hours"

---

## 🎯 Step 9: Practice Exercises

### Exercise 1: Create a Resource
Create a resource that shows the top 10 metrics by cardinality.

**Hint:**
```python
@mcp.resource("prometheus://metrics/high-cardinality")
async def get_high_cardinality_metrics() -> str:
    # Your code here
    pass
```

### Exercise 2: Create a Prompt
Create a prompt that analyzes cost optimization opportunities.

**Hint:**
```python
@mcp.prompt()
async def cost_optimization_prompt(service: str) -> str:
    # Fetch resource usage
    # Build analysis prompt
    pass
```

### Exercise 3: Combine Resources and Prompts
Use a resource to get data, then use a prompt to analyze it.

**Example conversation:**
```
User: "Analyze my system's resource usage"
AI: 
  1. Uses prometheus://dashboard/overview (resource)
  2. Uses performance_analysis_prompt (prompt)
  3. Combines insights
```

---

## 🐛 Troubleshooting

### Problem: "Cannot connect to Prometheus"

**Solution:**
```bash
# Check Prometheus is running
curl http://localhost:9090/-/healthy

# Verify URL is correct
echo $PROMETHEUS_URL

# Test a simple query
curl "http://localhost:9090/api/v1/query?query=up"
```

### Problem: "Resource returns empty data"

**Solution:**
- Check if the metric exists in Prometheus
- Test the PromQL query in Prometheus UI
- Verify the query syntax

### Problem: "Prompt doesn't work in VS Code"

**Solution:**
- Restart VS Code
- Check settings.json configuration
- Verify MCP server is running
- Check VS Code output panel for errors

---

## 📚 Next Steps

1. ✅ Read the full guide: `docs/PROMPTS_AND_RESOURCES_GUIDE.md`
2. ✅ Check the architecture: `docs/ARCHITECTURE.md`
3. ✅ Review quick reference: `docs/QUICK_REFERENCE.md`
4. ✅ Explore examples: `examples/`
5. ✅ Build your own prompts and resources!

---

## 🎉 Congratulations!

You now understand:
- ✅ What MCP prompts and resources are
- ✅ How they work in your server
- ✅ When to use each one
- ✅ How to test them
- ✅ How to create your own

**Keep experimenting and building!** 🚀

