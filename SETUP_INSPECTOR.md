# 🔍 Setting Up MCP Inspector

This guide explains how to set up and run the MCP Inspector for testing your Prometheus MCP Server.

## 📋 Prerequisites

- **Node.js** 22.7.5+ (for MCP Inspector)
- **Python** 3.10+ (for the MCP server)
- **npm** (comes with Node.js)

## 🚀 Quick Start

### 1. Install MCP Inspector

```bash
npm install @modelcontextprotocol/inspector
```

This will create a `node_modules/` folder (~143 MB).

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 3. Run the Inspector

```bash
# Make sure venv is activated
source venv/bin/activate

# Run the inspector
npx @modelcontextprotocol/inspector python -m prometheus_mcp_server.simple_server
```

The inspector will open at: `http://localhost:6274`

## 📁 Folder Structure

```
prometheus-mcp-server/
├── node_modules/          ← NPM packages (143 MB) - NOT in git
├── venv/                  ← Python venv (95 MB) - NOT in git
├── src/                   ← Source code
├── docs/                  ← Documentation
├── examples/              ← Demo scripts
├── package.json           ← NPM config (if created)
├── pyproject.toml         ← Python config
└── .gitignore             ← Excludes node_modules and venv
```

## 🧹 Cleanup

### Remove Virtual Environment
```bash
rm -rf venv
```

### Remove Node Modules
```bash
rm -rf node_modules
```

Both can be easily recreated with the commands above.

## 🔄 Recreating Environments

### Recreate Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Recreate Node Modules
```bash
npm install @modelcontextprotocol/inspector
```

## 🎯 Using the Inspector

Once running, you can:

1. **Test Resources** - Access data endpoints
2. **Test Prompts** - Test AI analysis templates
3. **Test Tools** - Execute actions
4. **View Capabilities** - See all available features

## 📝 Notes

- `node_modules/` is required for MCP Inspector (NPM-based)
- `venv/` is optional and can be recreated anytime
- Both are excluded from git (see `.gitignore`)
- The `run_inspector.sh` script automates the setup

## 🚀 Automated Setup

Use the provided script:

```bash
chmod +x run_inspector.sh
./run_inspector.sh
```

This will:
1. Activate the virtual environment
2. Start the MCP Inspector
3. Open it in your browser

## 🆘 Troubleshooting

### Node version too old
```bash
# Check your Node version
node --version

# Need 22.7.5+
# Update with: brew install node@22
```

### Python version too old
```bash
# Check your Python version
python3 --version

# Need 3.10+
# Update with: brew install python@3.13
```

### Port already in use
The inspector uses port 6274. If it's in use:
```bash
# Kill the process using the port
lsof -i :6274
kill -9 <PID>
```

### Permission denied on run_inspector.sh
```bash
chmod +x run_inspector.sh
```

## 📚 Resources

- [MCP Inspector Docs](https://modelcontextprotocol.io/docs/tools/inspector)
- [FastMCP Docs](https://github.com/jlowin/fastmcp)
- [Prometheus MCP Server](./README.md)

