#!/usr/bin/env python3
"""
MCP Server over HTTP for VS Code integration
This implements the MCP protocol over HTTP as expected by VS Code MCP client
"""

import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("puzzle-mcp-http-server")

# Load puzzle data
PUZZLE_DATA_PATH = Path(__file__).parent / "offline_verifier_generation.json"

class MCPHTTPServer:
    def __init__(self):
        self.app = FastAPI(title="Puzzle MCP Server", version="1.0.0")
        self.puzzle_data: Dict[str, Dict] = {}
        self.sessions: Dict[str, Dict] = {}
        self.setup_middleware()
        self.setup_routes()
        self.load_puzzle_data()
    
    def setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def load_puzzle_data(self):
        """Load puzzle data from JSON file"""
        try:
            with open(PUZZLE_DATA_PATH, 'r') as f:
                data = json.load(f)
            
            # Convert to dict format if needed
            if isinstance(data, list):
                self.puzzle_data = {str(i): puzzle for i, puzzle in enumerate(data)}
            else:
                self.puzzle_data = data
            
            logger.info(f"Loaded {len(self.puzzle_data)} puzzles")
        except Exception as e:
            logger.error(f"Failed to load puzzle data: {e}")
            self.puzzle_data = {}
    
    def setup_routes(self):
        """Setup MCP protocol routes"""
        
        @self.app.post("/")
        async def mcp_endpoint(request: Request):
            """Main MCP endpoint that handles all MCP requests"""
            try:
                body = await request.json()
                return await self.handle_mcp_request(body)
            except Exception as e:
                logger.error(f"Error handling MCP request: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "jsonrpc": "2.0",
                        "id": body.get("id") if 'body' in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": str(e)
                        }
                    }
                )
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "puzzles_loaded": len(self.puzzle_data),
                "active_sessions": len(self.sessions)
            }
    
    async def handle_mcp_request(self, request: Dict) -> Dict:
        """Handle MCP JSON-RPC requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"Handling MCP request: {method}")
        
        try:
            if method == "initialize":
                return await self.handle_initialize(request_id, params)
            elif method == "notifications/initialized":
                return {"jsonrpc": "2.0", "id": request_id, "result": {}}
            elif method == "tools/list":
                return await self.handle_tools_list(request_id)
            elif method == "tools/call":
                return await self.handle_tools_call(request_id, params)
            elif method == "resources/list":
                return await self.handle_resources_list(request_id)
            elif method == "resources/read":
                return await self.handle_resources_read(request_id, params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Error in method {method}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
    
    async def handle_initialize(self, request_id: int, params: Dict) -> Dict:
        """Handle MCP initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "puzzle-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    
    async def handle_tools_list(self, request_id: int) -> Dict:
        """Return available tools"""
        tools = [
            {
                "name": "create_session",
                "description": "Create a new puzzle session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "puzzle_count": {"type": "integer", "default": 5},
                        "min_correct": {"type": "integer", "default": 3}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "get_session_status",
                "description": "Get the status of a puzzle session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "submit_answer",
                "description": "Submit an answer for the current puzzle",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "answer": {"type": "string"}
                    },
                    "required": ["session_id", "answer"]
                }
            },
            {
                "name": "get_random_puzzle",
                "description": "Get a random puzzle",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
    
    async def handle_tools_call(self, request_id: int, params: Dict) -> Dict:
        """Handle tool calls"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "create_session":
            return await self.create_session(request_id, arguments)
        elif tool_name == "get_session_status":
            return await self.get_session_status(request_id, arguments)
        elif tool_name == "submit_answer":
            return await self.submit_answer(request_id, arguments)
        elif tool_name == "get_random_puzzle":
            return await self.get_random_puzzle(request_id, arguments)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
    
    async def create_session(self, request_id: int, args: Dict) -> Dict:
        """Create a new puzzle session"""
        session_id = args.get("session_id")
        puzzle_count = args.get("puzzle_count", 5)
        min_correct = args.get("min_correct", 3)
        
        # Select random puzzles
        import random
        puzzle_ids = random.sample(list(self.puzzle_data.keys()), min(puzzle_count, len(self.puzzle_data)))
        
        session = {
            "session_id": session_id,
            "puzzle_ids": puzzle_ids,
            "current_index": 0,
            "correct_answers": 0,
            "min_correct": min_correct,
            "completed": False
        }
        
        self.sessions[session_id] = session
        
        current_puzzle = self.puzzle_data[puzzle_ids[0]]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Created session '{session_id}' with {puzzle_count} puzzles. Need {min_correct} correct answers.\n\n" +
                               f"Puzzle 1/{puzzle_count}:\n{current_puzzle.get('question', 'No question available')}"
                    }
                ]
            }
        }
    
    async def get_session_status(self, request_id: int, args: Dict) -> Dict:
        """Get session status"""
        session_id = args.get("session_id")
        session = self.sessions.get(session_id)
        
        if not session:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Session {session_id} not found"
                }
            }
        
        current_puzzle_id = session["puzzle_ids"][session["current_index"]]
        current_puzzle = self.puzzle_data[current_puzzle_id]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Session: {session_id}\n" +
                               f"Progress: {session['current_index'] + 1}/{len(session['puzzle_ids'])}\n" +
                               f"Correct answers: {session['correct_answers']}/{session['min_correct']}\n" +
                               f"Completed: {session['completed']}\n\n" +
                               f"Current puzzle:\n{current_puzzle.get('question', 'No question available')}"
                    }
                ]
            }
        }
    
    async def submit_answer(self, request_id: int, args: Dict) -> Dict:
        """Submit an answer"""
        session_id = args.get("session_id")
        answer = args.get("answer")
        session = self.sessions.get(session_id)
        
        if not session:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Session {session_id} not found"
                }
            }
        
        current_puzzle_id = session["puzzle_ids"][session["current_index"]]
        current_puzzle = self.puzzle_data[current_puzzle_id]
        correct_answer = current_puzzle.get("solution", "").strip().lower()
        user_answer = answer.strip().lower()
        
        is_correct = user_answer == correct_answer
        if is_correct:
            session["correct_answers"] += 1
        
        # Move to next puzzle
        session["current_index"] += 1
        
        result_text = f"Answer: {answer}\n"
        result_text += f"Correct: {is_correct}\n"
        result_text += f"Expected: {correct_answer}\n\n"
        
        if session["current_index"] >= len(session["puzzle_ids"]):
            # Session complete
            session["completed"] = True
            if session["correct_answers"] >= session["min_correct"]:
                result_text += f"🎉 Session complete! You got {session['correct_answers']}/{session['min_correct']} correct!\n"
                result_text += "🔓 Secret unlocked: The key to solving puzzles is persistence and logical thinking!"
            else:
                result_text += f"Session complete. You got {session['correct_answers']}/{session['min_correct']} correct. Try again!"
        else:
            # Next puzzle
            next_puzzle_id = session["puzzle_ids"][session["current_index"]]
            next_puzzle = self.puzzle_data[next_puzzle_id]
            result_text += f"Next puzzle ({session['current_index'] + 1}/{len(session['puzzle_ids'])}):\n"
            result_text += next_puzzle.get('question', 'No question available')
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
        }
    
    async def get_random_puzzle(self, request_id: int, args: Dict) -> Dict:
        """Get a random puzzle"""
        import random
        puzzle_id = random.choice(list(self.puzzle_data.keys()))
        puzzle = self.puzzle_data[puzzle_id]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Random Puzzle (ID: {puzzle_id}):\n\n{puzzle.get('question', 'No question available')}\n\n" +
                               f"Solution: {puzzle.get('solution', 'No solution available')}"
                    }
                ]
            }
        }
    
    async def handle_resources_list(self, request_id: int) -> Dict:
        """List available resources"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": []
            }
        }
    
    async def handle_resources_read(self, request_id: int, params: Dict) -> Dict:
        """Read a resource"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": []
            }
        }

def main():
    parser = argparse.ArgumentParser(description="Puzzle MCP HTTP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    args = parser.parse_args()
    
    server = MCPHTTPServer()
    
    print(f"🧩 Starting Puzzle MCP HTTP Server on {args.host}:{args.port}")
    print(f"📊 Loaded {len(server.puzzle_data)} puzzles")
    print(f"🌐 MCP Endpoint: http://{args.host}:{args.port}/")
    print(f"🔍 Health Check: http://{args.host}:{args.port}/health")
    
    uvicorn.run(server.app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
