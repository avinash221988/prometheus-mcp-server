auggie mcp list

auggie mcp add prometheus-server -- /Users/abh551/prometheus-mcp-server/venv/bin/python -m prometheus_mcp_server.simple_server --prometheus-url https://platform-prometheus.sandpfm.cosmic.sky --alertmanager-url https://platform-alertmanager.sandpfm.cosmic.sky/ --timeout 30 --no-verify-ssl

auggie mcp add k8s-server -- /Users/abh551/prometheus-mcp-server/venv/bin/k8s-mcp-server


Using MCP on Auggie:

git clone https://github.com/avinash221988/prometheus-mcp-server.git
cd prometheus-mcp-server
./setup-mcp.sh