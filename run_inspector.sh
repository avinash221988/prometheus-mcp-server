#!/bin/bash

# Run MCP Inspector against Prometheus MCP Server

cd /Users/abh551/prometheus-mcp-server

# Use Node 22 (required for MCP Inspector)
export PATH="/opt/homebrew/opt/node@22/bin:$PATH"

# Use Python 3.13 (required for FastMCP)
PYTHON_BIN="/opt/homebrew/bin/python3.13"

# Create Python venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment with Python 3.13..."
    $PYTHON_BIN -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
echo "Installing dependencies..."
pip install -e . --quiet 2>/dev/null

# Run the inspector
echo ""
echo "=========================================="
echo "Starting MCP Inspector..."
echo "=========================================="
echo "Node version: $(node --version)"
echo "Python version: $(python --version)"
echo ""
echo "🚀 MCP Inspector will be available at:"
echo "   http://localhost:6274"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

npx @modelcontextprotocol/inspector python -m prometheus_mcp_server.simple_server

