# 🧩 Puzzle MCP Server

A complete **Model Context Protocol (MCP)** server implementation for serving academic puzzles to AI agents.

## 📁 Project Structure

```
MCP/
├── puzzle_mcp_server.py          # Core MCP server (stdio protocol)
├── puzzle_http_server.py         # HTTP REST API server
├── puzzle_websocket_server.py    # WebSocket MCP server
├── offline_verifier_generation.json  # Puzzle database (279 puzzles)
├── requirements.txt               # Python dependencies
├── 
├── # Testing & Examples
├── test_http_deployment.py       # HTTP server test suite
├── simple_test.py                # Quick HTTP server verification
├── test_puzzle_server.py         # Core server logic tests
├── test_server_logic.py          # Individual component tests
├── example_external_agent.py     # Agent integration example
├── mcp_config.json              # MCP configuration template
├── 
├── # Docker Deployment
├── Dockerfile                    # Container image
├── docker-compose.yml           # Multi-service deployment
├── nginx.conf                   # Reverse proxy configuration
├── 
└── # Documentation
    ├── README_MCP.md             # MCP protocol details
    ├── AGENT_CONFIGURATION.md    # Agent setup guide
    ├── DEPLOYMENT_SUCCESS.md     # Complete deployment guide
    ├── REMOTE_DEPLOYMENT.md      # Cloud deployment options
    └── SERVER_STATUS.md          # Server monitoring
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd MCP
pip install -r requirements.txt
```

### 2. Choose Your Deployment Method

#### **Local MCP (Claude Desktop, etc.)**
```bash
python puzzle_mcp_server.py
```

#### **HTTP REST API (Web Agents)**
```bash
python puzzle_http_server.py --host 0.0.0.0 --port 8000
```

#### **WebSocket MCP (Real-time Agents)**
```bash
python puzzle_websocket_server.py --host 0.0.0.0 --port 8001
```

#### **Docker Production**
```bash
docker-compose up -d
```

## 🧪 Testing

### Quick Verification
```bash
python simple_test.py
```

### Full Test Suite
```bash
python test_http_deployment.py
python test_puzzle_server.py
```

## 🔧 Features

### **Puzzle Database**
- 🎯 **279 academic puzzles** from research dataset
- 🏆 **24 curated high-quality puzzles** for optimal experience
- 🔍 **Dynamic puzzle selection** with difficulty management
- ✅ **Answer verification** with partial matching

### **Session Management**
- 🎮 **Multi-puzzle sessions** with configurable requirements
- 📊 **Progress tracking** with real-time status
- 🎉 **Secret unlock mechanism** for successful completion
- 🔒 **Session isolation** for concurrent users

### **Protocol Support**
- 📟 **MCP Stdio** - Local agents, containers
- 🌐 **HTTP REST** - Web services, external APIs
- ⚡ **WebSocket** - Real-time streaming applications

## 🌐 Agent Integration

### **Claude Desktop**
```json
{
  "mcpServers": {
    "puzzle-server": {
      "command": "python",
      "args": ["/path/to/MCP/puzzle_mcp_server.py"]
    }
  }
}
```

### **Custom HTTP Agent**
```python
import requests

# Create session
response = requests.post("http://your-server/api/sessions", json={
    "session_id": "my_session",
    "puzzle_count": 5,
    "min_correct": 3
})

# Get puzzle and submit answer
session = response.json()
puzzle = session['current_puzzle']
```

### **WebSocket Agent**
```python
import websockets
import json

async with websockets.connect("ws://your-server:8001") as ws:
    # Send MCP initialize
    await ws.send(json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05"}
    }))
```

## 🛠 Available Tools

### **MCP Protocol Tools**
- `create_session` - Start new puzzle session
- `get_session_status` - Check progress
- `submit_answer` - Submit puzzle solution
- `get_random_puzzle` - Fetch random puzzle
- `get_puzzle_by_id` - Get specific puzzle
- `get_hint` - Request puzzle hint
- `list_curated_puzzles` - High-quality puzzle list
- `end_session` - Terminate session

### **HTTP REST Endpoints**
- `GET /health` - Server status
- `POST /api/sessions` - Create session
- `GET /api/sessions/{id}` - Session status
- `POST /api/sessions/{id}/answer` - Submit answer
- `GET /api/puzzles/random` - Random puzzle
- `GET /api/puzzles/{id}` - Specific puzzle
- `GET /docs` - Interactive API docs

## 🔒 Production Deployment

### **Security Features**
- 🔐 CORS configuration for web access
- 🛡️ Input validation and sanitization
- 📊 Health monitoring and logging
- 🚦 Rate limiting ready (configurable)

### **Cloud Platforms**
- ☁️ **AWS EC2/ECS** - Scalable compute
- 🌍 **Google Cloud Run** - Serverless deployment
- 🌊 **DigitalOcean** - Simple droplet setup
- 🔷 **Azure Container Instances** - Managed containers

## 📚 Documentation

- **[MCP Protocol Details](README_MCP.md)** - Technical implementation
- **[Agent Configuration](AGENT_CONFIGURATION.md)** - Setup guides
- **[Deployment Guide](DEPLOYMENT_SUCCESS.md)** - Complete deployment
- **[Remote Deployment](REMOTE_DEPLOYMENT.md)** - Cloud platforms
- **[Server Monitoring](SERVER_STATUS.md)** - Health & metrics

## ⚡ Performance

- **Concurrent Sessions**: Unlimited (memory permitting)
- **Response Time**: < 50ms typical
- **Memory Usage**: ~20MB base + sessions
- **Scalability**: Horizontal with load balancer

## 🎯 Use Cases

### **Educational**
- 🎓 AI reasoning assessment
- 🧠 Logic puzzle training
- 📚 Academic research tools

### **Development**
- 🤖 Agent capability testing
- 🔬 MCP protocol development
- 📊 Benchmarking AI systems

### **Production**
- 🏢 Enterprise AI tools
- 🌐 Web-based puzzle platforms
- 📱 Mobile app backends

---

**Ready to serve puzzles to AI agents!** 🚀

Choose your deployment method and start integrating with your favorite AI agents.
