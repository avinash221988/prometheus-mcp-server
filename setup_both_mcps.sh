#!/bin/bash

# Setup script for both Prometheus and Kubernetes MCP servers

set -e

echo "🚀 Setting up Prometheus + Kubernetes MCP Servers"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -e .

# Verify installations
echo ""
echo "✅ Verifying installations..."
echo ""

# Check Prometheus MCP
echo "Prometheus MCP:"
python3 -c "import prometheus_mcp_server; print(f'  Version: {prometheus_mcp_server.__version__}')"
python3 -c "import httpx; print('  httpx: OK')"
python3 -c "import fastmcp; print('  fastmcp: OK')"

echo ""
echo "Kubernetes MCP:"
python3 -c "import kubernetes_mcp_server; print(f'  Version: {kubernetes_mcp_server.__version__}')"
python3 -c "from kubernetes import client, config; print('  kubernetes: OK')"

echo ""
echo "🎯 Testing Kubernetes connectivity..."
python3 -c "
from kubernetes import client, config
try:
    config.load_kube_config()
    v1 = client.CoreV1Api()
    namespaces = v1.list_namespace(limit=1)
    print('  ✅ Kubernetes connection successful!')
    print(f'  Current context: {config.list_kube_config_contexts()[1][\"name\"]}')
except Exception as e:
    print(f'  ⚠️  Warning: Could not connect to Kubernetes: {e}')
    print('  Make sure kubectl is configured and you have access to a cluster')
"

echo ""
echo "=================================================="
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Configure both MCP servers in VS Code settings"
echo "2. Reload VS Code"
echo "3. Start using both servers together!"
echo ""
echo "📖 See docs/MULTI_MCP_INTEGRATION.md for usage examples"
echo "=================================================="

