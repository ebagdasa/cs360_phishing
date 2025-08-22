#!/usr/bin/env python3
"""
MCP Server for serving academic puzzles from the existing puzzle database.
This server exposes tools to fetch random puzzles, check answers, and manage puzzle sessions.
"""

import json
import random
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("puzzle-server")

# Load puzzle data
PUZZLE_DATA_PATH = Path(__file__).parent / "offline_verifier_generation.json"

class PuzzleServer:
    def __init__(self):
        self.server = Server("puzzle-server")
        self.puzzle_data: Dict[str, Dict] = {}
        self.sessions: Dict[str, Dict] = {}
        self.load_puzzle_data()
        self.setup_handlers()
    
    def load_puzzle_data(self):
        """Load puzzle data from JSON file"""
        try:
            with open(PUZZLE_DATA_PATH, 'r', encoding='utf-8') as f:
                self.puzzle_data = json.load(f)
            logger.info(f"Loaded {len(self.puzzle_data)} puzzles")
        except Exception as e:
            logger.error(f"Failed to load puzzle data: {e}")
            self.puzzle_data = {}
    
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available puzzle resources"""
            return [
                Resource(
                    uri="puzzle://data/all",
                    name="All Puzzles",
                    description="Complete puzzle database with questions and solutions",
                    mimeType="application/json"
                ),
                Resource(
                    uri="puzzle://data/curated",
                    name="Curated Puzzles",
                    description="Curated subset of puzzles used in the web interface",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read puzzle resource data"""
            if uri == "puzzle://data/all":
                return json.dumps(self.puzzle_data, indent=2)
            elif uri == "puzzle://data/curated":
                # Return curated list from server.js
                curated_ids = ['1', '154', '157', '159', '165', '171', '173', '174', 
                              '178', '180', '182', '184', '185', '190', '191', '192', 
                              '200', '201', '202', '207', '208', '209', '212', '213']
                curated_puzzles = {id: self.puzzle_data[id] for id in curated_ids if id in self.puzzle_data}
                return json.dumps(curated_puzzles, indent=2)
            else:
                raise ValueError(f"Unknown resource URI: {uri}")
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available puzzle tools"""
            return [
                Tool(
                    name="get_random_puzzle",
                    description="Get a random puzzle from the curated collection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "exclude_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of puzzle IDs to exclude from selection"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_puzzle_by_id",
                    description="Get a specific puzzle by its ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "puzzle_id": {
                                "type": "string",
                                "description": "The ID of the puzzle to retrieve"
                            }
                        },
                        "required": ["puzzle_id"]
                    }
                ),
                Tool(
                    name="check_puzzle_answer",
                    description="Check if an answer is correct for a given puzzle",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "puzzle_id": {
                                "type": "string",
                                "description": "The ID of the puzzle"
                            },
                            "answer": {
                                "type": "string",
                                "description": "The answer to check"
                            }
                        },
                        "required": ["puzzle_id", "answer"]
                    }
                ),
                Tool(
                    name="create_puzzle_session",
                    description="Create a new puzzle session with multiple puzzles",
                    inputSchema={
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
                ),
                Tool(
                    name="get_session_status",
                    description="Get the current status of a puzzle session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "The session ID"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="submit_session_answer",
                    description="Submit an answer for the current puzzle in a session",
                    inputSchema={
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
                ),
                Tool(
                    name="list_puzzle_categories",
                    description="List all unique subject domains found in puzzles",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="search_puzzles",
                    description="Search puzzles by subject domain or keywords",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Subject domain to search for (e.g., 'computer science', 'mathematics')"
                            },
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Keywords to search for in puzzle questions"
                            },
                            "limit": {
                                "type": "integer",
                                "default": 10,
                                "description": "Maximum number of results to return"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool calls"""
            try:
                if name == "get_random_puzzle":
                    return await self.get_random_puzzle(arguments)
                elif name == "get_puzzle_by_id":
                    return await self.get_puzzle_by_id(arguments)
                elif name == "check_puzzle_answer":
                    return await self.check_puzzle_answer(arguments)
                elif name == "create_puzzle_session":
                    return await self.create_puzzle_session(arguments)
                elif name == "get_session_status":
                    return await self.get_session_status(arguments)
                elif name == "submit_session_answer":
                    return await self.submit_session_answer(arguments)
                elif name == "list_puzzle_categories":
                    return await self.list_puzzle_categories(arguments)
                elif name == "search_puzzles":
                    return await self.search_puzzles(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def get_random_puzzle(self, arguments: dict) -> list[TextContent]:
        """Get a random puzzle from the curated collection"""
        # Curated list (same as in server.js)
        curated_ids = ['1', '154', '157', '159', '165', '171', '173', '174', 
                      '178', '180', '182', '184', '185', '190', '191', '192', 
                      '200', '201', '202', '207', '208', '209', '212', '213']
        
        exclude_ids = arguments.get('exclude_ids', [])
        available_ids = [id for id in curated_ids if id in self.puzzle_data and id not in exclude_ids]
        
        if not available_ids:
            return [TextContent(type="text", text="No puzzles available with current filters")]
        
        puzzle_id = random.choice(available_ids)
        puzzle = self.puzzle_data[puzzle_id]
        
        result = {
            "puzzle_id": puzzle_id,
            "question": puzzle["question"],
            "solution": puzzle["solution"]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def get_puzzle_by_id(self, arguments: dict) -> list[TextContent]:
        """Get a specific puzzle by ID"""
        puzzle_id = arguments["puzzle_id"]
        
        if puzzle_id not in self.puzzle_data:
            return [TextContent(type="text", text=f"Puzzle ID '{puzzle_id}' not found")]
        
        puzzle = self.puzzle_data[puzzle_id]
        result = {
            "puzzle_id": puzzle_id,
            "question": puzzle["question"],
            "solution": puzzle["solution"]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def check_puzzle_answer(self, arguments: dict) -> list[TextContent]:
        """Check if an answer is correct"""
        puzzle_id = arguments["puzzle_id"]
        user_answer = arguments["answer"].strip().lower()
        
        if puzzle_id not in self.puzzle_data:
            return [TextContent(type="text", text=f"Puzzle ID '{puzzle_id}' not found")]
        
        correct_answer = self.puzzle_data[puzzle_id]["solution"].strip().lower()
        is_correct = user_answer == correct_answer
        
        result = {
            "puzzle_id": puzzle_id,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def create_puzzle_session(self, arguments: dict) -> list[TextContent]:
        """Create a new puzzle session"""
        session_id = arguments["session_id"]
        puzzle_count = arguments.get("puzzle_count", 5)
        min_correct = arguments.get("min_correct", 2)
        
        # Select random puzzles from curated list
        curated_ids = ['1', '154', '157', '159', '165', '171', '173', '174', 
                      '178', '180', '182', '184', '185', '190', '191', '192', 
                      '200', '201', '202', '207', '208', '209', '212', '213']
        
        available_ids = [id for id in curated_ids if id in self.puzzle_data]
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
        
        result = {
            "session_id": session_id,
            "total_puzzles": len(selected_ids),
            "min_correct": min_correct,
            "current_puzzle": {
                "puzzle_id": selected_ids[0],
                "question": first_puzzle["question"],
                "question_number": 1
            }
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def get_session_status(self, arguments: dict) -> list[TextContent]:
        """Get session status"""
        session_id = arguments["session_id"]
        
        if session_id not in self.sessions:
            return [TextContent(type="text", text=f"Session '{session_id}' not found")]
        
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
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def submit_session_answer(self, arguments: dict) -> list[TextContent]:
        """Submit an answer for the current puzzle in a session"""
        session_id = arguments["session_id"]
        user_answer = arguments["answer"].strip().lower()
        
        if session_id not in self.sessions:
            return [TextContent(type="text", text=f"Session '{session_id}' not found")]
        
        session = self.sessions[session_id]
        
        if session["completed"]:
            return [TextContent(type="text", text="Session already completed")]
        
        if session["current_index"] >= len(session["puzzle_ids"]):
            return [TextContent(type="text", text="No more puzzles in session")]
        
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
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def list_puzzle_categories(self, arguments: dict) -> list[TextContent]:
        """List all unique subject domains found in puzzles"""
        domains = set()
        
        for puzzle in self.puzzle_data.values():
            question = puzzle.get("question", "").lower()
            # Extract domain mentions from questions
            for line in question.split('\n'):
                if 'subdomain' in line:
                    # Find domain name before 'subdomain'
                    parts = line.split('subdomain')
                    if parts:
                        domain_part = parts[0].strip()
                        # Extract the domain name (last word before subdomain)
                        words = domain_part.split()
                        if words:
                            domain = words[-1].strip('•: ')
                            if domain:
                                domains.add(domain)
        
        result = {
            "categories": sorted(list(domains)),
            "total_categories": len(domains)
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def search_puzzles(self, arguments: dict) -> list[TextContent]:
        """Search puzzles by domain or keywords"""
        domain = arguments.get("domain", "").lower()
        keywords = [kw.lower() for kw in arguments.get("keywords", [])]
        limit = arguments.get("limit", 10)
        
        results = []
        
        for puzzle_id, puzzle in self.puzzle_data.items():
            question = puzzle.get("question", "").lower()
            
            # Check domain filter
            if domain and domain not in question:
                continue
            
            # Check keywords
            if keywords:
                if not any(keyword in question for keyword in keywords):
                    continue
            
            results.append({
                "puzzle_id": puzzle_id,
                "question": puzzle["question"],
                "solution": puzzle["solution"]
            })
            
            if len(results) >= limit:
                break
        
        result = {
            "results": results,
            "total_found": len(results),
            "search_criteria": {
                "domain": domain,
                "keywords": keywords
            }
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def main():
    """Run the MCP server"""
    puzzle_server = PuzzleServer()
    
    # Import here to avoid circular imports
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await puzzle_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="puzzle-server",
                server_version="1.0.0",
                capabilities=puzzle_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
