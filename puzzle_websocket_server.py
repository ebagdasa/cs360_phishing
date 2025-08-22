#!/usr/bin/env python3
"""
WebSocket-based MCP Server for remote deployment.
This version implements the full MCP protocol over WebSocket for remote connections.
"""

import json
import asyncio
import logging
import websockets
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("puzzle-websocket-server")

# Load puzzle data
PUZZLE_DATA_PATH = Path(__file__).parent / "public" / "new_offline_verifier_generation.json"

class MCPWebSocketServer:
    def __init__(self):
        self.puzzle_data: Dict[str, Dict] = {}
        self.sessions: Dict[str, Dict] = {}
        self.load_puzzle_data()
    
    def load_puzzle_data(self):
        """Load puzzle data from JSON file"""
        try:
            with open(PUZZLE_DATA_PATH, 'r', encoding='utf-8') as f:
                self.puzzle_data = json.load(f)
            logger.info(f"Loaded {len(self.puzzle_data)} puzzles")
        except Exception as e:
            logger.error(f"Failed to load puzzle data: {e}")
            self.puzzle_data = {}
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        client_id = str(uuid.uuid4())
        logger.info(f"Client {client_id} connected from {websocket.remote_address}")
        
        try:
            # Send initialization message
            await websocket.send(json.dumps({
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "listChanged": True
                        },
                        "resources": {
                            "subscribe": True,
                            "listChanged": True
                        }
                    },
                    "serverInfo": {
                        "name": "puzzle-websocket-server",
                        "version": "1.0.0"
                    }
                }
            }))
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    response = await self.handle_message(data, client_id)
                    if response:
                        await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        },
                        "id": None
                    }
                    await websocket.send(json.dumps(error_response))
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        },
                        "id": data.get("id") if isinstance(data, dict) else None
                    }
                    await websocket.send(json.dumps(error_response))
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error with client {client_id}: {e}")
    
    async def handle_message(self, data: dict, client_id: str):
        """Handle incoming MCP message"""
        method = data.get("method")
        params = data.get("params", {})
        msg_id = data.get("id")
        
        try:
            if method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "tools": [
                            {
                                "name": "get_random_puzzle",
                                "description": "Get a random puzzle from the curated collection",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "exclude_ids": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "List of puzzle IDs to exclude from selection"
                                        }
                                    }
                                }
                            },
                            {
                                "name": "create_puzzle_session",
                                "description": "Create a new puzzle session with multiple puzzles",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "session_id": {
                                            "type": "string",
                                            "description": "Unique identifier for the session"
                                        },
                                        "puzzle_count": {
                                            "type": "integer",
                                            "default": 5,
                                            "description": "Number of puzzles in the session"
                                        },
                                        "min_correct": {
                                            "type": "integer",
                                            "default": 2,
                                            "description": "Minimum correct answers required"
                                        }
                                    },
                                    "required": ["session_id"]
                                }
                            },
                            {
                                "name": "get_session_status",
                                "description": "Get the current status of a puzzle session",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "session_id": {
                                            "type": "string",
                                            "description": "The session ID"
                                        }
                                    },
                                    "required": ["session_id"]
                                }
                            },
                            {
                                "name": "submit_session_answer",
                                "description": "Submit an answer for the current puzzle in a session",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "session_id": {
                                            "type": "string",
                                            "description": "The session ID"
                                        },
                                        "answer": {
                                            "type": "string",
                                            "description": "The answer to submit"
                                        }
                                    },
                                    "required": ["session_id", "answer"]
                                }
                            }
                        ]
                    },
                    "id": msg_id
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "get_random_puzzle":
                    result = await self.get_random_puzzle(arguments)
                elif tool_name == "create_puzzle_session":
                    result = await self.create_puzzle_session(arguments)
                elif tool_name == "get_session_status":
                    result = await self.get_session_status(arguments)
                elif tool_name == "submit_session_answer":
                    result = await self.submit_session_answer(arguments)
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    },
                    "id": msg_id
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": msg_id
                }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": msg_id
            }
    
    async def get_random_puzzle(self, arguments: dict):
        """Get a random puzzle from the curated collection"""
        curated_ids = ['1', '154', '157', '159', '165', '171', '173', '174', 
                      '178', '180', '182', '184', '185', '190', '191', '192', 
                      '200', '201', '202', '207', '208', '209', '212', '213']
        
        exclude_ids = arguments.get('exclude_ids', [])
        available_ids = [id for id in curated_ids if id in self.puzzle_data and id not in exclude_ids]
        
        if not available_ids:
            raise ValueError("No puzzles available with current filters")
        
        import random
        puzzle_id = random.choice(available_ids)
        puzzle = self.puzzle_data[puzzle_id]
        
        return {
            "puzzle_id": puzzle_id,
            "question": puzzle["question"],
            "solution": puzzle["solution"]
        }
    
    async def create_puzzle_session(self, arguments: dict):
        """Create a new puzzle session"""
        session_id = arguments["session_id"]
        puzzle_count = arguments.get("puzzle_count", 5)
        min_correct = arguments.get("min_correct", 2)
        
        # Select random puzzles from curated list
        curated_ids = ['1', '154', '157', '159', '165', '171', '173', '174', 
                      '178', '180', '182', '184', '185', '190', '191', '192', 
                      '200', '201', '202', '207', '208', '209', '212', '213']
        
        available_ids = [id for id in curated_ids if id in self.puzzle_data]
        import random
        selected_ids = random.sample(available_ids, min(puzzle_count, len(available_ids)))
        
        # Create session
        self.sessions[session_id] = {
            "puzzle_ids": selected_ids,
            "current_index": 0,
            "correct_answers": 0,
            "min_correct": min_correct,
            "completed": False,
            "answers": []
        }
        
        # Get first puzzle
        first_puzzle = self.puzzle_data[selected_ids[0]]
        
        return {
            "session_id": session_id,
            "total_puzzles": len(selected_ids),
            "min_correct": min_correct,
            "current_puzzle": {
                "puzzle_id": selected_ids[0],
                "question": first_puzzle["question"],
                "question_number": 1
            }
        }
    
    async def get_session_status(self, arguments: dict):
        """Get session status"""
        session_id = arguments["session_id"]
        
        if session_id not in self.sessions:
            raise ValueError(f"Session '{session_id}' not found")
        
        session = self.sessions[session_id]
        
        result = {
            "session_id": session_id,
            "completed": session["completed"],
            "current_question": session["current_index"] + 1,
            "total_questions": len(session["puzzle_ids"]),
            "correct_answers": session["correct_answers"],
            "min_correct": session["min_correct"],
            "secret_revealed": session["correct_answers"] >= session["min_correct"]
        }
        
        if not session["completed"] and session["current_index"] < len(session["puzzle_ids"]):
            current_puzzle_id = session["puzzle_ids"][session["current_index"]]
            current_puzzle = self.puzzle_data[current_puzzle_id]
            result["current_puzzle"] = {
                "puzzle_id": current_puzzle_id,
                "question": current_puzzle["question"]
            }
        
        return result
    
    async def submit_session_answer(self, arguments: dict):
        """Submit an answer for the current puzzle in a session"""
        session_id = arguments["session_id"]
        user_answer = arguments["answer"].strip().lower()
        
        if session_id not in self.sessions:
            raise ValueError(f"Session '{session_id}' not found")
        
        session = self.sessions[session_id]
        
        if session["completed"]:
            raise ValueError("Session already completed")
        
        if session["current_index"] >= len(session["puzzle_ids"]):
            raise ValueError("No more puzzles in session")
        
        # Check current puzzle answer
        current_puzzle_id = session["puzzle_ids"][session["current_index"]]
        correct_answer = self.puzzle_data[current_puzzle_id]["solution"].strip().lower()
        is_correct = user_answer == correct_answer
        
        # Record answer
        session["answers"].append({
            "puzzle_id": current_puzzle_id,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })
        
        if is_correct:
            session["correct_answers"] += 1
        
        # Move to next puzzle
        session["current_index"] += 1
        
        # Check if session is completed
        if session["current_index"] >= len(session["puzzle_ids"]):
            session["completed"] = True
        
        result = {
            "session_id": session_id,
            "answer_correct": is_correct,
            "correct_answers": session["correct_answers"],
            "completed": session["completed"],
            "secret_revealed": session["correct_answers"] >= session["min_correct"]
        }
        
        # Add next puzzle if not completed
        if not session["completed"]:
            next_puzzle_id = session["puzzle_ids"][session["current_index"]]
            next_puzzle = self.puzzle_data[next_puzzle_id]
            result["next_puzzle"] = {
                "puzzle_id": next_puzzle_id,
                "question": next_puzzle["question"],
                "question_number": session["current_index"] + 1
            }
        
        if session["completed"] and result["secret_revealed"]:
            result["secret_message"] = "We are currently clean on OPSEC"
        
        return result

async def main():
    """Start the WebSocket server"""
    server = MCPWebSocketServer()
    
    import argparse
    parser = argparse.ArgumentParser(description="Puzzle WebSocket MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind to")
    
    args = parser.parse_args()
    
    print(f"🧩 Starting Puzzle WebSocket MCP Server on {args.host}:{args.port}")
    print(f"📊 Loaded {len(server.puzzle_data)} puzzles")
    print(f"🔌 WebSocket URL: ws://{args.host}:{args.port}")
    print("🛑 Press Ctrl+C to stop")
    
    async with websockets.serve(server.handle_client, args.host, args.port):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
