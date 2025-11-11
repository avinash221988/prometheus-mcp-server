#!/bin/bash

# Run MCP Inspector against Prometheus MCP Server
# This script starts the MCP Inspector in the background with proper environment configuration
#
# Usage:
#   ./run_inspector.sh                                    # Uses default http://localhost:9090
#   ./run_inspector.sh https://your-prometheus-url.com   # Uses custom Prometheus URL
#
# Environment variables:
#   PROMETHEUS_URL - Set to override the Prometheus URL

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Set Prometheus URL from argument or environment variable
if [ -n "$1" ]; then
    PROMETHEUS_URL="$1"
else
    PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
fi

# Use latest Node.js from Homebrew (required for MCP Inspector)
export PATH="/opt/homebrew/bin:$PATH"

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

# Check if already running
if lsof -i :6277 > /dev/null 2>&1; then
    echo "⚠️  Inspector is already running on port 6277"
    echo ""
    echo "🚀 MCP Inspector is available at:"
    echo "   http://localhost:6274"
    echo ""
    echo "To stop it, run: pkill -f inspector"
    exit 0
fi

echo "🚀 Starting MCP Inspector in background..."
echo "Using Prometheus URL: $PROMETHEUS_URL"
echo ""

# Run in background and save PID
# Pass PROMETHEUS_URL via the -e flag to the inspector
# Use python directly with the full path to avoid shell parsing issues
npx @modelcontextprotocol/inspector -e "PROMETHEUS_URL=$PROMETHEUS_URL" "$SCRIPT_DIR/venv/bin/python" -m prometheus_mcp_server.simple_server > /tmp/mcp_inspector.log 2>&1 &
INSPECTOR_PID=$!

# Wait a moment for it to start
sleep 3

# Check if it started successfully
if ps -p $INSPECTOR_PID > /dev/null; then
    echo "✅ Inspector started successfully (PID: $INSPECTOR_PID)"
    echo ""
    echo "🌐 MCP Inspector is available at:"
    echo "   http://localhost:6274"
    echo ""
    echo "📋 To view logs:"
    echo "   tail -f /tmp/mcp_inspector.log"
    echo ""
    echo "🛑 To stop it:"
    echo "   pkill -f inspector"
    echo "   or"
    echo "   kill $INSPECTOR_PID"
else
    echo "❌ Failed to start inspector. Check logs:"
    cat /tmp/mcp_inspector.log
    exit 1
fi

