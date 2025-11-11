# 🔍 MCP Inspector Setup & Usage Guide

Complete guide for setting up and running the MCP Inspector to test your Prometheus MCP Server.

---

## ⚡ Quick Start (Automated)

The easiest way to get started is using the provided automation script:

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

## 📋 Prerequisites

- **Node.js** 22.7.5+ (for MCP Inspector)
- **Python** 3.13+ (for FastMCP)
- **npm** (comes with Node.js)

---

## 🚀 Manual Setup (If Not Using Script)

### 1. Install MCP Inspector

```bash
npm install @modelcontextprotocol/inspector
```

This will create a `node_modules/` folder (~143 MB).

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3.13 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 3. Run the Inspector

```bash
# Make sure venv is activated
source venv/bin/activate

# Set your Prometheus URL
export PROMETHEUS_URL="https://your-prometheus-url.com"

# Run the inspector
npx @modelcontextprotocol/inspector python -m prometheus_mcp_server.simple_server

or try 

npx @modelcontextprotocol/inspector -e "PROMETHEUS_URL=https://your-prometheus-url.com"
```

The inspector will open at: `http://localhost:6274`

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

## 📋 How the Automation Works

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

## 📁 Folder Structure

```
prometheus-mcp-server/
├── node_modules/          ← NPM packages (143 MB) - NOT in git
├── venv/                  ← Python venv (95 MB) - NOT in git
├── src/                   ← Source code
├── docs/                  ← Documentation
├── examples/              ← Demo scripts
├── run_inspector.sh       ← Main automation script
├── mcp_server_wrapper.sh  ← Wrapper for env vars
├── package.json           ← NPM config (if created)
├── pyproject.toml         ← Python config
└── .gitignore             ← Excludes node_modules and venv
```

---

## 🧹 Cleanup & Maintenance

### Remove Virtual Environment
```bash
rm -rf venv
```

### Remove Node Modules
```bash
rm -rf node_modules
```

Both can be easily recreated with the commands above.

### Recreate Python Environment
```bash
python3.13 -m venv venv
source venv/bin/activate
pip install -e .
```

### Recreate Node Modules
```bash
npm install @modelcontextprotocol/inspector
```

---

## 🐛 Troubleshooting

### Inspector won't start
Check the logs:
```bash
cat /tmp/mcp_inspector.log
```

### Port already in use
The inspector uses port 6274. If it's in use:
```bash
# Kill the old process
pkill -f inspector
sleep 2
./run_inspector.sh
```

Or manually:
```bash
lsof -i :6274
kill -9 <PID>
```

### Module not found error
The venv might be corrupted. Recreate it:
```bash
rm -rf venv
./run_inspector.sh
```

### Node version too old
```bash
# Check your Node version
node --version

# Need 22.7.5+
# Update with: brew install node@22
```

### Python version error
Make sure Python 3.13 is installed:
```bash
/opt/homebrew/bin/python3.13 --version

# If not installed:
# brew install python@3.13
```

### Permission denied on run_inspector.sh
```bash
chmod +x run_inspector.sh
chmod +x mcp_server_wrapper.sh
```

### Prometheus connection failed
Make sure you're passing the correct Prometheus URL:
```bash
./run_inspector.sh "https://your-prometheus-url.com"
```

Or set the environment variable:
```bash
export PROMETHEUS_URL="https://your-prometheus-url.com"
./run_inspector.sh
```

---

## 📝 Notes

- The script runs the inspector in the **background**, so your terminal is free
- Logs are saved to `/tmp/mcp_inspector.log` for debugging
- The script checks if it's already running to prevent duplicates
- All paths are relative, so you can run it from any directory
- The venv is created with Python 3.13 (required for FastMCP)
- `node_modules/` is required for MCP Inspector (NPM-based)
- `venv/` is optional and can be recreated anytime
- Both are excluded from git (see `.gitignore`)

---

## 🎯 Next Steps

1. Run `./run_inspector.sh "https://your-prometheus-url.com"`
2. Open the URL in your browser
3. Click on "Resources" tab to test resources
4. Click on "Prompts" tab to test prompts
5. Click on "Tools" tab to test tools

---

## 📚 Resources

- [MCP Inspector Docs](https://modelcontextprotocol.io/docs/tools/inspector)
- [FastMCP Docs](https://github.com/jlowin/fastmcp)
- [Prometheus MCP Server](./README.md)

Happy testing! 🎉

