#!/bin/bash
# Startup script for Puzzle MCP Server

echo "🧩 Starting Puzzle MCP Server..."
echo "================================"

# Check if we're in the right directory
if [ ! -f "puzzle_mcp_server.py" ]; then
    echo "❌ Error: puzzle_mcp_server.py not found"
    echo "Please run this script from the openai_assistant directory"
    exit 1
fi

# Check if puzzle data exists
if [ ! -f "public/new_offline_verifier_generation.json" ]; then
    echo "❌ Error: Puzzle data file not found"
    echo "Expected: public/new_offline_verifier_generation.json"
    exit 1
fi

echo "✅ Puzzle data found ($(wc -l < public/new_offline_verifier_generation.json) lines)"

# Check Python environment
if command -v conda &> /dev/null; then
    echo "✅ Using conda environment"
    PYTHON_CMD="/opt/miniconda3/bin/conda run -p /opt/miniconda3 --no-capture-output python"
else
    echo "✅ Using system Python"
    PYTHON_CMD="python"
fi

echo "🚀 Starting MCP server..."
echo "   Server will accept connections on stdio"
echo "   Press Ctrl+C to stop"
echo ""

# Start the server
exec $PYTHON_CMD puzzle_mcp_server.py
