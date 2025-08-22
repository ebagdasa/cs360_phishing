# OpenAI Assistant Server

A simple server for interacting with OpenAI's Assistant API, plus a complete **Model Context Protocol (MCP)** implementation for serving academic puzzles to AI agents.

## 📁 Project Structure

```
├── server.js                    # Express.js OpenAI Assistant API server
├── public/                      # Web interface files
├── package.json                 # Node.js dependencies
├── MCP/                         # 🧩 Complete MCP Server Implementation
│   ├── puzzle_mcp_server.py     # Core MCP server (stdio)
│   ├── puzzle_http_server.py    # HTTP REST API server
│   ├── puzzle_websocket_server.py # WebSocket MCP server
│   ├── offline_verifier_generation.json # 279 academic puzzles
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Container deployment
│   ├── docker-compose.yml      # Multi-service deployment
│   └── README.md               # 📖 Complete MCP documentation
└── README.md                   # This file
```

## 🚀 Quick Start

### OpenAI Assistant Server

1. Clone this repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file in the root directory with your OpenAI API key and Assistant ID:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ASSISTANT_ID=asst_fh1JTqS8faXwsYZHNalfXR0L
   PORT=3000
   ```
4. Start the server:
   ```bash
   npm start
   ```
   Or for development with auto-restart:
   ```bash
   npm run dev
   ```

### 🧩 MCP Puzzle Server

**See the complete documentation in [`MCP/README.md`](MCP/README.md)**

#### Quick MCP Server Start:
```bash
cd MCP
pip install -r requirements.txt

# Choose your deployment:
python puzzle_mcp_server.py      # Local MCP (Claude Desktop)
python puzzle_http_server.py     # HTTP API (Web agents)
python puzzle_websocket_server.py # WebSocket (Real-time)
docker-compose up -d             # Production deployment
```

## 🌟 Features

### OpenAI Assistant Server
- Express.js server to interact with OpenAI Assistant API
- Simple chat interface
- Persistent conversations using OpenAI Threads
- RESTful API endpoints for thread management

### 🧩 MCP Puzzle Server
- **279 academic puzzles** from research dataset
- **Multiple protocols**: MCP stdio, HTTP REST, WebSocket
- **Session management** with progress tracking
- **Docker deployment** ready for production
- **Agent integration** examples for Claude Desktop and custom agents

## 🚀 Deployment

### OpenAI Assistant Server
To deploy this on your VM:

1. Clone the repository on your VM
2. Install dependencies with `npm install`
3. Set up your `.env` file with your API key and Assistant ID
4. Start the server with `npm start` or use a process manager like PM2:
   ```bash
   npm install -g pm2
   pm2 start server.js --name "openai-assistant"
   ```
5. Set up a reverse proxy with Nginx or similar if needed

### 🧩 MCP Server Deployment
See [`MCP/DEPLOYMENT_SUCCESS.md`](MCP/DEPLOYMENT_SUCCESS.md) for complete deployment options:
- **Local deployment** for Claude Desktop
- **HTTP API deployment** for web agents
- **Docker deployment** for production
- **Cloud platform deployment** (AWS, GCP, Azure, DigitalOcean)

## 📚 Usage

### OpenAI Assistant Interface
- Visit `http://localhost:3000` (or your VM's address) to access the chat interface
- Type messages in the input field and press Send or hit Enter
- The assistant will respond based on how you've configured it in OpenAI

### 🧩 MCP Server Integration
- **Claude Desktop**: Add MCP server to configuration
- **Custom Agents**: Use HTTP API endpoints
- **Real-time Apps**: Connect via WebSocket

## 📖 API Documentation

### OpenAI Assistant Endpoints
- `POST /api/threads` - Create a new thread
- `POST /api/threads/:threadId/messages` - Send a message to a thread
- `GET /api/threads/:threadId/messages` - Get all messages in a thread

### 🧩 MCP Server Endpoints
- `GET /health` - Server health check
- `POST /api/sessions` - Create puzzle session
- `GET /api/puzzles/random` - Get random puzzle
- `POST /api/sessions/{id}/answer` - Submit answer
- See [`MCP/README.md`](MCP/README.md) for complete API documentation

## 📄 License

MIT
