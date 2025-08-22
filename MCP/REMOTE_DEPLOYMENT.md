# Remote Deployment Guide for Puzzle MCP Server

## 🌐 Overview

This guide explains how to deploy the Puzzle MCP Server on remote servers and register it for external agent access. The server can be deployed in multiple modes:

1. **HTTP REST API** - For web-based agents and HTTP clients
2. **WebSocket MCP** - For real-time MCP protocol communication
3. **Stdio MCP** - For local/container-based MCP clients
4. **Docker Deployment** - For scalable cloud deployment

## 🚀 Deployment Options

### Option 1: HTTP REST API Server

**Best for:** Web agents, HTTP-based integrations, testing

```bash
# Local testing
python puzzle_http_server.py --host 0.0.0.0 --port 8000

# Production deployment
python puzzle_http_server.py --host 0.0.0.0 --port 8000
```

**API Endpoints:**
- `GET /health` - Health check
- `GET /api/puzzles/random` - Get random puzzle
- `POST /api/sessions` - Create puzzle session
- `GET /api/sessions/{session_id}` - Get session status
- `POST /api/sessions/{session_id}/answer` - Submit answer
- `GET /docs` - Interactive API documentation

**Example Usage:**
```bash
# Create session
curl -X POST "http://your-server:8000/api/sessions" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "agent_001", "puzzle_count": 5, "min_correct": 2}'

# Get session status
curl "http://your-server:8000/api/sessions/agent_001"

# Submit answer
curl -X POST "http://your-server:8000/api/sessions/agent_001/answer" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "agent_001", "answer": "isles"}'
```

### Option 2: WebSocket MCP Server

**Best for:** Real-time MCP protocol, streaming communication

```bash
# Start WebSocket server
python puzzle_websocket_server.py --host 0.0.0.0 --port 8765
```

**Connection URL:** `ws://your-server:8765`

**MCP Protocol Support:**
- Full JSON-RPC 2.0 over WebSocket
- Standard MCP tool calling
- Real-time bidirectional communication

### Option 3: Docker Deployment

**Best for:** Production, scalability, cloud deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t puzzle-mcp-server .
docker run -p 8000:8000 -p 8765:8765 puzzle-mcp-server
```

**Services:**
- `puzzle-http-server` on port 8000
- `puzzle-websocket-server` on port 8765
- `nginx` reverse proxy on port 80
- `puzzle-stdio-server` for container communication

## 🔧 MCP Client Registration

### For Claude Desktop

Add to `~/.config/claude-desktop/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "puzzle-server-remote": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/cli",
        "websocket",
        "ws://your-server:8765"
      ]
    }
  }
}
```

### For Custom MCP Clients

#### HTTP Client
```python
import httpx

class HTTPMCPClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def create_session(self, session_id, puzzle_count=5, min_correct=2):
        response = await self.client.post(f"{self.base_url}/api/sessions", json={
            "session_id": session_id,
            "puzzle_count": puzzle_count,
            "min_correct": min_correct
        })
        return response.json()
    
    async def submit_answer(self, session_id, answer):
        response = await self.client.post(
            f"{self.base_url}/api/sessions/{session_id}/answer",
            json={"session_id": session_id, "answer": answer}
        )
        return response.json()
```

#### WebSocket Client
```python
import asyncio
import json
import websockets

class WebSocketMCPClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
    
    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
    
    async def call_tool(self, tool_name, arguments):
        message = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": "1"
        }
        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()
        return json.loads(response)
```

### For LangChain Integration

```python
from langchain.tools import BaseTool
import httpx

class PuzzleMCPTool(BaseTool):
    name = "puzzle_solver"
    description = "Solve academic puzzles to unlock secrets"
    base_url: str = "http://your-server:8000"
    
    def _run(self, action: str, **kwargs):
        # Implement HTTP calls to your server
        pass
```

### For OpenAI Assistants

```json
{
  "type": "function",
  "function": {
    "name": "create_puzzle_session",
    "description": "Create a new puzzle solving session",
    "parameters": {
      "type": "object",
      "properties": {
        "session_id": {"type": "string"},
        "puzzle_count": {"type": "integer", "default": 5},
        "min_correct": {"type": "integer", "default": 2}
      },
      "required": ["session_id"]
    }
  }
}
```

## 🌍 Cloud Deployment

### AWS Deployment

#### Using AWS ECS (Fargate)
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t puzzle-mcp-server .
docker tag puzzle-mcp-server:latest <account>.dkr.ecr.us-east-1.amazonaws.com/puzzle-mcp-server:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/puzzle-mcp-server:latest

# Deploy with ECS task definition
```

#### Using AWS Lambda (for HTTP API)
```bash
# Package for Lambda
pip install -t lambda-package/ fastapi uvicorn[standard] mangum
cp puzzle_http_server.py lambda-package/
cp -r public/ lambda-package/

# Create Lambda handler
echo "from mangum import Mangum; from puzzle_http_server import app; handler = Mangum(app)" > lambda-package/lambda_function.py
```

### Google Cloud Platform

#### Using Cloud Run
```bash
# Deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/puzzle-mcp-server
gcloud run deploy puzzle-mcp-server --image gcr.io/PROJECT_ID/puzzle-mcp-server --platform managed --port 8000
```

### Microsoft Azure

#### Using Container Instances
```bash
# Deploy to Azure Container Instances
az container create \
  --resource-group myResourceGroup \
  --name puzzle-mcp-server \
  --image puzzle-mcp-server:latest \
  --ports 8000 8765 \
  --cpu 1 --memory 1
```

### DigitalOcean

#### Using App Platform
```yaml
# .do/app.yaml
name: puzzle-mcp-server
services:
- name: web
  source_dir: /
  github:
    repo: your-username/puzzle-mcp-server
    branch: main
  run_command: python puzzle_http_server.py --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
```

## 🔒 Security Considerations

### Environment Variables
```bash
# Set in production
export PUZZLE_DATA_PATH="/secure/path/to/puzzles.json"
export MAX_SESSIONS="1000"
export RATE_LIMIT="100"
export API_KEY="your-secret-key"
```

### Nginx Configuration (Production)
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }
    
    location /ws {
        proxy_pass http://127.0.0.1:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 📊 Monitoring and Logging

### Health Checks
```bash
# HTTP endpoint
curl http://your-server:8000/health

# WebSocket check
echo '{"jsonrpc":"2.0","method":"tools/list","id":"1"}' | websocat ws://your-server:8765
```

### Logging Configuration
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/puzzle-mcp-server.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics
```python
# Add to servers for monitoring
from prometheus_client import Counter, Histogram, start_http_server

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')
```

## 🧪 Testing Remote Deployment

### Automated Tests
```bash
# Test HTTP API
curl -f http://your-server:8000/health
curl -X POST http://your-server:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","puzzle_count":1,"min_correct":1}'

# Test WebSocket
echo '{"jsonrpc":"2.0","method":"tools/list","id":"1"}' | websocat ws://your-server:8765
```

### Load Testing
```bash
# Using wrk
wrk -t12 -c400 -d30s http://your-server:8000/health

# Using artillery
artillery quick --count 10 --num 100 http://your-server:8000/health
```

## 🚀 Agent Integration Examples

### Simple HTTP Agent
```python
import asyncio
import httpx

async def solve_puzzles():
    async with httpx.AsyncClient() as client:
        # Create session
        session = await client.post("http://your-server:8000/api/sessions", json={
            "session_id": "agent_001",
            "puzzle_count": 5,
            "min_correct": 2
        })
        
        session_data = session.json()
        session_id = session_data["session_id"]
        
        while True:
            # Get status
            status = await client.get(f"http://your-server:8000/api/sessions/{session_id}")
            status_data = status.json()
            
            if status_data["completed"] or status_data["secret_revealed"]:
                if status_data["secret_revealed"]:
                    print(f"🎉 Secret unlocked!")
                break
            
            # Solve current puzzle
            puzzle = status_data["current_puzzle"]["question"]
            answer = solve_puzzle_logic(puzzle)  # Your solving logic
            
            # Submit answer
            result = await client.post(
                f"http://your-server:8000/api/sessions/{session_id}/answer",
                json={"session_id": session_id, "answer": answer}
            )
            
            result_data = result.json()
            if result_data.get("secret_revealed"):
                print(f"🔓 Secret: {result_data.get('secret_message')}")
                break

asyncio.run(solve_puzzles())
```

## 📋 Deployment Checklist

- [ ] **Server Setup**
  - [ ] Python 3.12+ installed
  - [ ] Dependencies installed (`pip install -r requirements.txt`)
  - [ ] Puzzle data file accessible
  - [ ] Firewall configured (ports 8000, 8765)

- [ ] **Security**
  - [ ] SSL/TLS certificates configured
  - [ ] Rate limiting enabled
  - [ ] API authentication (if required)
  - [ ] CORS settings configured

- [ ] **Monitoring**
  - [ ] Health check endpoint working
  - [ ] Logging configured
  - [ ] Metrics collection setup
  - [ ] Alert system configured

- [ ] **Testing**
  - [ ] HTTP endpoints tested
  - [ ] WebSocket connection tested
  - [ ] Load testing completed
  - [ ] End-to-end agent integration tested

- [ ] **Documentation**
  - [ ] API documentation accessible (`/docs`)
  - [ ] Client integration examples provided
  - [ ] Troubleshooting guide created

## 🎯 Success Metrics

Your remote deployment is successful when:

✅ **Health checks pass:** `curl http://your-server:8000/health` returns 200
✅ **API accessible:** External agents can create sessions and submit answers  
✅ **WebSocket working:** MCP clients can connect and call tools
✅ **Secrets unlockable:** Agents can solve puzzles and get "We are currently clean on OPSEC"
✅ **Performance adequate:** Server handles expected load without issues
✅ **Monitoring active:** Logs and metrics are being collected

---

**Your Puzzle MCP Server is now ready for global agent access! 🌍🤖**
