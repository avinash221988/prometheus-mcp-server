# 🏗️ MCP Architecture - Prompts & Resources

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AI Assistant                             │
│                    (GitHub Copilot, Claude, etc.)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ MCP Protocol
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Your MCP Server                               │
│                (prometheus-mcp-server)                           │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Resources   │  │   Prompts    │  │    Tools     │         │
│  │  (3 total)   │  │  (2 total)   │  │  (6 total)   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                            │                                     │
│                   ┌────────▼────────┐                           │
│                   │ PrometheusClient │                           │
│                   └────────┬────────┘                           │
└────────────────────────────┼────────────────────────────────────┘
                             │
                             │ HTTP/API
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      Prometheus Server                           │
│                    (Your monitoring system)                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagrams

### Resource Flow (Read Data)

```
┌──────┐     1. Request Resource      ┌─────────────┐
│  AI  │ ─────────────────────────────▶│ MCP Server  │
└──────┘                               └──────┬──────┘
                                              │
                                              │ 2. Execute
                                              │    @mcp.resource
                                              │
                                       ┌──────▼──────┐
                                       │ Prometheus  │
                                       │   Query     │
                                       └──────┬──────┘
                                              │
                                              │ 3. Return
                                              │    JSON data
┌──────┐     4. Receive Data          ┌──────▼──────┐
│  AI  │ ◀─────────────────────────────│ MCP Server  │
└──────┘                               └─────────────┘
```

**Example:**
```
AI: "Show me prometheus://dashboard/overview"
 ↓
MCP Server: get_dashboard_overview()
 ↓
Prometheus: Execute 4 queries (CPU, Memory, Disk, Alerts)
 ↓
MCP Server: Return combined JSON
 ↓
AI: "Here's your system overview: CPU 45%, Memory 62%..."
```

---

### Prompt Flow (AI Analysis)

```
┌──────┐     1. Request Analysis      ┌─────────────┐
│  AI  │ ─────────────────────────────▶│ MCP Server  │
└──────┘                               └──────┬──────┘
                                              │
                                              │ 2. Execute
                                              │    @mcp.prompt
                                              │
                                       ┌──────▼──────┐
                                       │ Prometheus  │
                                       │   Query     │
                                       └──────┬──────┘
                                              │
                                              │ 3. Build
                                              │    Prompt
┌──────┐     4. Receive Prompt        ┌──────▼──────┐
│  AI  │ ◀─────────────────────────────│ MCP Server  │
└──┬───┘                               └─────────────┘
   │
   │ 5. AI analyzes
   │    the prompt
   │
   ▼
┌──────┐
│ User │ ◀─── 6. AI returns analysis
└──────┘
```

**Example:**
```
AI: "Analyze the 'HighMemoryUsage' alert"
 ↓
MCP Server: analyze_alert_prompt("HighMemoryUsage")
 ↓
Prometheus: Query ALERTS{alertname="HighMemoryUsage"}
 ↓
MCP Server: Build structured prompt with data + instructions
 ↓
AI: Receives prompt, analyzes data
 ↓
User: Gets detailed analysis with root cause, impact, actions
```

---

## 🎯 Component Breakdown

### 1. Resources (Data Providers)

```python
@mcp.resource("prometheus://alerts/firing")
async def get_firing_alerts() -> str:
    # 1. Query Prometheus
    result = await prometheus.query('ALERTS{alertstate="firing"}')
    
    # 2. Return JSON
    return json.dumps(result, indent=2)
```

**Characteristics:**
- ✅ Read-only
- ✅ Returns raw data
- ✅ URI-based access
- ✅ Can have dynamic parameters
- ✅ Synchronous data fetch

**Your Resources:**
```
prometheus://alerts/firing          → Firing alerts
prometheus://metrics/{metric_name}  → Specific metric
prometheus://dashboard/overview     → System overview
```

---

### 2. Prompts (Analysis Templates)

```python
@mcp.prompt()
async def analyze_alert_prompt(alert_name: str, timerange: str = "1h") -> str:
    # 1. Fetch relevant data
    alert_data = await prometheus.query(f'ALERTS{{alertname="{alert_name}"}}')
    
    # 2. Build structured prompt
    return f"""
    Analyze this Prometheus alert:
    
    Alert: {alert_name}
    Data: {json.dumps(alert_data, indent=2)}
    
    Please provide:
    1. Root cause analysis
    2. Impact assessment
    3. Recommended actions
    """
```

**Characteristics:**
- ✅ Fetches data + provides instructions
- ✅ Returns formatted prompt text
- ✅ Guides AI analysis
- ✅ Can combine multiple data sources
- ✅ Structures expected output

**Your Prompts:**
```
analyze_alert_prompt           → Alert analysis
performance_analysis_prompt    → Service performance
```

---

### 3. Tools (Actions)

```python
@mcp.tool()
async def prometheus_query(query: str) -> str:
    # Execute action and return result
    result = await prometheus.query(query)
    return json.dumps(result, indent=2)
```

**Characteristics:**
- ✅ Can read AND write
- ✅ Execute actions
- ✅ Direct function calls
- ✅ Can have side effects

---

## 🔀 Interaction Patterns

### Pattern 1: Simple Data Retrieval
```
User → "Show firing alerts"
     → Resource: prometheus://alerts/firing
     → Returns: Raw alert data
```

### Pattern 2: AI-Guided Analysis
```
User → "Why is this alert firing?"
     → Prompt: analyze_alert_prompt
     → Fetches: Alert data
     → Returns: Structured prompt
     → AI: Analyzes and explains
```

### Pattern 3: Combined Approach
```
User → "Analyze system performance"
     → Resource: prometheus://dashboard/overview (get current state)
     → Prompt: performance_analysis_prompt (detailed analysis)
     → Tool: prometheus_query (custom queries if needed)
     → AI: Combines all data for comprehensive analysis
```

---

## 📊 Data Transformation

### Resource Data Flow
```
Prometheus Metric
    ↓
PromQL Query: 'ALERTS{alertstate="firing"}'
    ↓
Prometheus Response: {status: "success", data: {...}}
    ↓
JSON Serialization: json.dumps(result, indent=2)
    ↓
MCP Response: String containing formatted JSON
    ↓
AI Receives: Structured data ready for processing
```

### Prompt Data Flow
```
User Request: "Analyze HighMemoryUsage alert"
    ↓
Prompt Function: analyze_alert_prompt("HighMemoryUsage")
    ↓
Data Fetch: prometheus.query('ALERTS{alertname="HighMemoryUsage"}')
    ↓
Prompt Building: Template + Data + Instructions
    ↓
MCP Response: Complete prompt text
    ↓
AI Processing: Analyzes data according to instructions
    ↓
User Receives: Detailed analysis with recommendations
```

---

## 🎨 Design Patterns

### Resource Pattern: Dashboard Aggregation
```python
@mcp.resource("prometheus://dashboard/overview")
async def get_dashboard_overview() -> str:
    # Aggregate multiple metrics
    queries = {
        "cpu": "...",
        "memory": "...",
        "disk": "...",
        "alerts": "..."
    }
    
    overview = {}
    for name, query in queries.items():
        overview[name] = await prometheus.query(query)
    
    return json.dumps(overview, indent=2)
```

**Use case:** Provide comprehensive view in single request

---

### Prompt Pattern: Structured Analysis
```python
@mcp.prompt()
async def analyze_alert_prompt(alert_name: str, timerange: str = "1h") -> str:
    # 1. Fetch data
    data = await prometheus.query(...)
    
    # 2. Structure analysis request
    return f"""
    Context: {alert_name} over {timerange}
    Data: {data}
    
    Analysis Required:
    1. Root cause
    2. Impact
    3. Actions
    4. Prevention
    """
```

**Use case:** Guide AI to provide consistent, thorough analysis

---

## 🚀 Scalability Considerations

### Resource Caching
```python
# Future enhancement: Add caching
@mcp.resource("prometheus://dashboard/overview")
async def get_dashboard_overview() -> str:
    # Could add TTL cache here
    # cache_key = "dashboard_overview"
    # if cached := cache.get(cache_key, ttl=60):
    #     return cached
    
    result = await fetch_dashboard_data()
    # cache.set(cache_key, result)
    return result
```

### Prompt Optimization
```python
# Fetch multiple metrics in parallel
async def performance_analysis_prompt(service: str) -> str:
    # Instead of sequential queries
    results = await asyncio.gather(
        prometheus.query(cpu_query),
        prometheus.query(memory_query),
        prometheus.query(requests_query),
        prometheus.query(errors_query)
    )
    # Build prompt with all results
```

---

## 📈 Extension Ideas

### New Resource Ideas
```python
@mcp.resource("prometheus://targets/health")
@mcp.resource("prometheus://rules/recording")
@mcp.resource("prometheus://metrics/top-cpu")
@mcp.resource("prometheus://timeseries/{metric}/{duration}")
```

### New Prompt Ideas
```python
@mcp.prompt()
async def capacity_planning_prompt(...)

@mcp.prompt()
async def incident_investigation_prompt(...)

@mcp.prompt()
async def cost_optimization_prompt(...)
```

---

## 🎓 Key Takeaways

1. **Resources** = Data endpoints (like REST APIs)
2. **Prompts** = AI analysis templates (data + instructions)
3. **Tools** = Actions (can modify state)

4. **Resources** are for when you need the data
5. **Prompts** are for when you need AI to analyze the data

6. Both can fetch from Prometheus
7. Both return strings (JSON or prompt text)
8. Both are async functions

---

**Next:** Try the interactive demo!
```bash
python examples/demo_prompts_resources.py
```

