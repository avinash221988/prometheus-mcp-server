# 🎓 Your MCP Learning Path

## 📦 What I've Created For You

I've created a comprehensive learning package to help you understand and demonstrate MCP prompts and resources:

### 📚 Documentation (4 files)

1. **[docs/GETTING_STARTED_TUTORIAL.md](docs/GETTING_STARTED_TUTORIAL.md)** ⭐ START HERE
   - Step-by-step tutorial for beginners
   - Hands-on exercises
   - Troubleshooting guide
   - Practice exercises

2. **[docs/PROMPTS_AND_RESOURCES_GUIDE.md](docs/PROMPTS_AND_RESOURCES_GUIDE.md)**
   - Complete explanation of MCP concepts
   - Detailed breakdown of your implementation
   - Best practices
   - Practical examples

3. **[docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)**
   - Cheat sheet for quick lookup
   - All resources and prompts listed
   - Example conversations
   - Code snippets

4. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**
   - System architecture diagrams
   - Data flow explanations
   - Design patterns
   - Extension ideas

### 🧪 Demo Script

**[examples/demo_prompts_resources.py](examples/demo_prompts_resources.py)**
- Interactive demo program
- Tests all resources
- Tests all prompts
- Shows comparisons
- Menu-driven interface

---

## 🚀 Recommended Learning Path

### Step 1: Quick Overview (5 minutes)
```bash
# Read the quick reference
cat docs/QUICK_REFERENCE.md
```

### Step 2: Run Interactive Demo (10 minutes)
```bash
# Make sure Prometheus is running
export PROMETHEUS_URL=http://localhost:9090

# Run the demo
python examples/demo_prompts_resources.py

# Try all options:
# 1. Test all Resources
# 2. Test all Prompts
# 3. Compare Resources vs Prompts
```

### Step 3: Read the Tutorial (20 minutes)
```bash
# Follow the step-by-step guide
cat docs/GETTING_STARTED_TUTORIAL.md
```

### Step 4: Deep Dive (30 minutes)
```bash
# Read the complete guide
cat docs/PROMPTS_AND_RESOURCES_GUIDE.md

# Understand the architecture
cat docs/ARCHITECTURE.md
```

### Step 5: Hands-On Practice (30 minutes)
- Test with MCP Inspector
- Try in VS Code with GitHub Copilot
- Create your own resource
- Create your own prompt

---

## 🎯 What You'll Learn

### Understanding MCP Primitives

**Resources** (Data Sources)
- What they are: Read-only data endpoints
- When to use: Need current state/data
- Your implementation: 3 resources
  - `prometheus://alerts/firing`
  - `prometheus://metrics/{metric_name}`
  - `prometheus://dashboard/overview`

**Prompts** (AI Analysis Templates)
- What they are: Data + AI instructions
- When to use: Need AI analysis
- Your implementation: 2 prompts
  - `analyze_alert_prompt`
  - `performance_analysis_prompt`

**Tools** (Actions)
- What they are: Executable functions
- When to use: Need to perform actions
- Your implementation: 6 tools
  - `prometheus_query`
  - `prometheus_health`
  - `prometheus_cpu`
  - `prometheus_memory`
  - `prometheus_services`
  - `alertmanager_silence`

---

## 💡 Key Concepts You'll Master

### 1. Resource URIs
```
prometheus://alerts/firing          → Static resource
prometheus://metrics/{metric_name}  → Dynamic resource with parameter
prometheus://dashboard/overview     → Aggregated resource
```

### 2. Prompt Structure
```python
@mcp.prompt()
async def my_prompt(param: str) -> str:
    # 1. Fetch data
    data = await prometheus.query(...)
    
    # 2. Build prompt with instructions
    return f"""
    Context: {param}
    Data: {data}
    
    Please analyze:
    1. Point 1
    2. Point 2
    """
```

### 3. When to Use What
- **Resource**: "Show me the data"
- **Prompt**: "Analyze this for me"
- **Tool**: "Do this action"

---

## 🧪 Testing Methods

### Method 1: Interactive Demo Script
```bash
python examples/demo_prompts_resources.py
```
**Best for:** Understanding how things work

### Method 2: MCP Inspector
```bash
npx @modelcontextprotocol/inspector prometheus-mcp-server
```
**Best for:** Visual testing and exploration

### Method 3: VS Code Integration
```json
{
  "github.copilot.chat.tools": {
    "prometheus": {
      "command": "prometheus-mcp-server",
      "env": {"PROMETHEUS_URL": "http://localhost:9090"}
    }
  }
}
```
**Best for:** Real-world usage

### Method 4: Direct Code Testing
```python
# Import and test directly
from prometheus_mcp_server.simple_server import get_firing_alerts
result = await get_firing_alerts()
```
**Best for:** Development and debugging

---

## 📊 Your Implementation Summary

### Resources You Have (3)

| URI | Function | Returns |
|-----|----------|---------|
| `prometheus://alerts/firing` | `get_firing_alerts()` | Currently firing alerts |
| `prometheus://metrics/{metric_name}` | `get_metric(metric_name)` | Specific metric data |
| `prometheus://dashboard/overview` | `get_dashboard_overview()` | System overview |

### Prompts You Have (2)

| Name | Function | Purpose |
|------|----------|---------|
| Alert Analysis | `analyze_alert_prompt(alert_name, timerange)` | Root cause analysis |
| Performance Analysis | `performance_analysis_prompt(service, duration)` | Service performance |

### Tools You Have (6)

| Name | Function | Purpose |
|------|----------|---------|
| Query | `prometheus_query(query)` | Execute PromQL |
| Health | `prometheus_health()` | Check health |
| CPU | `prometheus_cpu()` | Get CPU metrics |
| Memory | `prometheus_memory()` | Get memory metrics |
| Services | `prometheus_services()` | Check services |
| Silence | `alertmanager_silence(...)` | Silence alerts |

---

## 🎨 Example Use Cases

### Use Case 1: Quick Status Check
```
User: "What's my system status?"
→ Uses: prometheus://dashboard/overview (Resource)
→ Gets: CPU, Memory, Disk, Alerts in one call
```

### Use Case 2: Alert Investigation
```
User: "Why is the HighMemoryUsage alert firing?"
→ Uses: analyze_alert_prompt (Prompt)
→ Gets: Root cause, impact, actions, prevention
```

### Use Case 3: Performance Analysis
```
User: "Analyze my API service performance"
→ Uses: performance_analysis_prompt (Prompt)
→ Gets: Trends, bottlenecks, capacity, optimization
```

### Use Case 4: Custom Query
```
User: "Show me HTTP request rate for the last 5 minutes"
→ Uses: prometheus_query (Tool)
→ Executes: rate(http_requests_total[5m])
```

---

## 🚀 Next Steps After Learning

### 1. Create Custom Resources
Add resources for your specific needs:
- Top CPU consumers
- High cardinality metrics
- Custom dashboards
- Service-specific views

### 2. Create Custom Prompts
Add prompts for your workflows:
- Capacity planning
- Cost optimization
- Incident investigation
- SLA compliance

### 3. Integrate with Your Workflow
- Add to VS Code
- Use in CI/CD
- Automate monitoring
- Build custom dashboards

### 4. Share with Your Team
- Document your custom additions
- Create team-specific prompts
- Build shared resources
- Establish best practices

---

## 📖 Quick Command Reference

```bash
# Start MCP server
prometheus-mcp-server

# Run interactive demo
python examples/demo_prompts_resources.py

# Test with inspector
npx @modelcontextprotocol/inspector prometheus-mcp-server

# Check Prometheus connection
curl $PROMETHEUS_URL/-/healthy

# View documentation
cat docs/QUICK_REFERENCE.md
cat docs/GETTING_STARTED_TUTORIAL.md
cat docs/PROMPTS_AND_RESOURCES_GUIDE.md
cat docs/ARCHITECTURE.md
```

---

## 🎯 Success Criteria

You'll know you've mastered MCP prompts and resources when you can:

- ✅ Explain the difference between resources, prompts, and tools
- ✅ Create a new resource for your use case
- ✅ Create a new prompt for AI analysis
- ✅ Test your implementations with MCP Inspector
- ✅ Use them effectively in VS Code with GitHub Copilot
- ✅ Understand when to use each primitive
- ✅ Debug issues with your MCP server

---

## 🆘 Getting Help

If you get stuck:

1. **Check the troubleshooting section** in `docs/GETTING_STARTED_TUTORIAL.md`
2. **Review the examples** in `docs/PROMPTS_AND_RESOURCES_GUIDE.md`
3. **Run the demo** to see working examples
4. **Check the architecture** to understand the flow
5. **Test with MCP Inspector** to see what's happening

---

## 🎉 You're Ready!

Start with:
```bash
python examples/demo_prompts_resources.py
```

Then read:
```bash
cat docs/GETTING_STARTED_TUTORIAL.md
```

**Happy Learning! 🚀**

