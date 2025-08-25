# Example configurations for the ADK agent to connect to the MCP server

## Configuration 1: StreamableHTTP (recommended for development/testing)
```python
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StreamableHttpServerParams,
)

async def get_tools_http():
    """Gets tools from MCP Server using StreamableHTTP."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StreamableHttpServerParams(
            url="http://localhost:8001/mcp",
        )
    )
    return tools, exit_stack
```

## Configuration 2: SSE (Server-Sent Events)
```python
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    SseServerParams,
)

async def get_tools_sse():
    """Gets tools from MCP Server using SSE."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://localhost:8001/sse",
        )
    )
    return tools, exit_stack
```

## Configuration 3: STDIO (recommended for production)
```python
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParams,
)

async def get_tools_stdio():
    """Gets tools from MCP Server using STDIO."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParams(
            command="python",
            args=["/path/to/mcp_server.py", "--transport", "stdio"],
        )
    )
    return tools, exit_stack
```

## Server Commands:

### Start HTTP Server (default):
```bash
python mcp_server.py --transport http --host 0.0.0.0 --port 8001
# or simply:
python mcp_server.py
```

### Start SSE Server:
```bash
python mcp_server.py --transport sse --host 0.0.0.0 --port 8001
```

### Start STDIO Server:
```bash
python mcp_server.py --transport stdio
```

### Custom Configuration Examples:
```bash
# HTTP on custom port
python mcp_server.py --transport http --host localhost --port 9001

# SSE on custom port  
python mcp_server.py --transport sse --host localhost --port 9002
```

## Benefits:

### StreamableHTTP:
- ✅ Easy to test and debug
- ✅ Can be accessed via REST clients  
- ✅ Good for development
- ✅ Supports multiple concurrent connections
- ✅ Modern HTTP-based protocol

### SSE (Server-Sent Events):
- ✅ Real-time bidirectional communication
- ✅ Built on standard HTTP
- ✅ Good for interactive applications
- ✅ Supports streaming responses
- ✅ Compatible with web browsers

### STDIO:
- ✅ Most efficient for single connections
- ✅ Best for production deployments
- ✅ Lowest resource overhead
- ✅ Standard MCP transport method
- ✅ Process-based isolation
