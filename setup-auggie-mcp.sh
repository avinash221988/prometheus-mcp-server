#!/bin/bash
# setup-mcp.sh - Run this to setup MCP servers for auggie

set -e

echo "🚀 Setting up Platform MCP Servers..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
fi

echo "📦 Installing dependencies..."
source "$SCRIPT_DIR/venv/bin/activate"
pip install -e "$SCRIPT_DIR" --quiet

auggie mcp remove prometheus-server 2>/dev/null || true
auggie mcp remove k8s-server 2>/dev/null || true

echo "🔧 Configuring auggie MCP servers..."

auggie mcp add prometheus-server -- "$SCRIPT_DIR/venv/bin/python" -m prometheus_mcp_server.simple_server \
  --prometheus-url https://platform-prometheus.sandpfm.cosmic.sky \
  --alertmanager-url https://platform-alertmanager.sandpfm.cosmic.sky/ \
  --timeout 30 \
  --no-verify-ssl

auggie mcp add k8s-server -- "$SCRIPT_DIR/venv/bin/k8s-mcp-server"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Make sure you're logged into the K8s cluster:"
echo "      oul -g sandbox
echo ""
echo "   2. Start using auggie:"
echo "      auggie chat \"Show me firing alerts\""
echo ""