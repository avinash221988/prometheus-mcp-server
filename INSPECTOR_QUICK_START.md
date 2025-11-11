# MCP Inspector Quick Start Guide

## 🚀 Start the Inspector

### Default (localhost Prometheus)
```bash
./run_inspector.sh
```

### With Custom Prometheus URL
```bash
./run_inspector.sh "https://your-prometheus-url.com"
```

That's it! The script will:
- ✅ Use Node 22 (required for MCP Inspector)
- ✅ Use Python 3.13 (required for FastMCP)
- ✅ Create venv if it doesn't exist
- ✅ Install dependencies
- ✅ Pass the Prometheus URL to the MCP server
- ✅ Start the inspector in the background
- ✅ Show you the URL to access it

---

## 🌐 Access the Inspector

After running the script, you'll see output like:

```
✅ Inspector started successfully (PID: 63546)

🌐 MCP Inspector is available at:
   http://localhost:6274
```

Open that URL in your browser. The token is automatically included in the URL.

---

## 📋 How It Works

### run_inspector.sh
1. **Navigates to the project directory** - Uses relative paths so it works from anywhere
2. **Sets up Node 22** - Required for MCP Inspector
3. **Sets up Python 3.13** - Required for FastMCP
4. **Creates venv** - Only if it doesn't exist
5. **Installs dependencies** - Runs `pip install -e .`
6. **Accepts Prometheus URL** - As first argument or via `PROMETHEUS_URL` env var
7. **Checks if already running** - Won't start duplicate instances
8. **Starts in background** - Doesn't block your terminal
9. **Logs to `/tmp/mcp_inspector.log`** - Easy to debug

### mcp_server_wrapper.sh
- **Wrapper script** that ensures environment variables are properly passed to the MCP server
- **Activates venv** with all dependencies
- **Sets PROMETHEUS_URL** from environment or uses default
- **Runs the MCP server** with proper configuration

---

## 🛑 Stop the Inspector

```bash
pkill -f inspector
```

Or use the PID shown when you started it:
```bash
kill 63546
```

---

## 📊 View Logs

```bash
tail -f /tmp/mcp_inspector.log
```

---

## 🔄 Run Again

If the inspector is already running, the script will detect it and show you the URL:

```
⚠️  Inspector is already running on port 6277

🚀 MCP Inspector is available at:
   http://localhost:6274

To stop it, run: pkill -f inspector
```

---

## 🧪 Test Your MCP Server

In the Inspector UI, you can:

### Resources
- `prometheus://alerts/firing` - Get firing alerts
- `prometheus://metrics/up` - Get metric data
- `prometheus://dashboard/overview` - System overview

### Prompts
- `analyze_alert_prompt` - Alert analysis
- `performance_analysis_prompt` - Performance analysis

### Tools
- `prometheus_query` - Execute PromQL
- `prometheus_health` - Check health
- `prometheus_cpu` - CPU metrics
- `prometheus_memory` - Memory metrics
- `prometheus_services` - Service status
- `alertmanager_silence` - Silence alerts

---

## 🔧 Environment Variables

### PROMETHEUS_URL
Controls which Prometheus instance the MCP server connects to.

**Set via command line:**
```bash
./run_inspector.sh "https://your-prometheus-url.com"
```

**Set via environment variable:**
```bash
export PROMETHEUS_URL="https://your-prometheus-url.com"
./run_inspector.sh
```

**Default:**
```
http://localhost:9090
```

---

## ⚙️ Requirements

The script automatically handles these, but here's what's needed:

- **Node 22.7.5+** - Installed at `/opt/homebrew/opt/node@22/bin/node`
- **Python 3.13** - Installed at `/opt/homebrew/bin/python3.13`
- **npm packages** - `node_modules/` directory with `@modelcontextprotocol/inspector`

---

## 🐛 Troubleshooting

### Inspector won't start
Check the logs:
```bash
cat /tmp/mcp_inspector.log
```

### Port already in use
Kill the old process:
```bash
pkill -f inspector
sleep 2
./run_inspector.sh
```

### Module not found error
The venv might be corrupted. Recreate it:
```bash
rm -rf venv
./run_inspector.sh
```

### Python version error
Make sure Python 3.13 is installed:
```bash
/opt/homebrew/bin/python3.13 --version
```

---

## 📝 Notes

- The script runs the inspector in the **background**, so your terminal is free
- Logs are saved to `/tmp/mcp_inspector.log` for debugging
- The script checks if it's already running to prevent duplicates
- All paths are relative, so you can run it from any directory
- The venv is created with Python 3.13 (required for FastMCP)

---

## 🎯 Next Steps

1. Run `./run_inspector.sh`
2. Open the URL in your browser
3. Click on "Resources" tab to test resources
4. Click on "Prompts" tab to test prompts
5. Click on "Tools" tab to test tools

Happy testing! 🎉

