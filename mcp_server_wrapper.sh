#!/bin/bash

# Wrapper script to run the MCP server with proper environment variables
# This ensures PROMETHEUS_URL is passed through to the Python process

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate venv
source venv/bin/activate

# Set Prometheus URL (use environment variable or default)
export PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"

# Run the MCP server
python -m prometheus_mcp_server.simple_server

