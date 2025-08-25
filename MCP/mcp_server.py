# Puzzle MCP Server

import argparse
import contextlib
import json
import random
import logging
from pathlib import Path
from typing import Dict, Optional
from collections.abc import AsyncIterator

import anyio
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from mcp.shared.exceptions import McpError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("puzzle-mcp-server")

# Load puzzle data
PUZZLE_DATA_PATH = Path(__file__).parent / "offline_verifier_generation.json"

# Global storage for sessions and puzzle data
puzzle_data: Dict[str, Dict] = {}
sessions: Dict[str, Dict] = {}

# Curated list of puzzle IDs to use (same as Express server)
ALLOWED_PUZZLE_IDS = ['1', '154', '157', '159', '165', '171', '173', '174', '178', '180', '182', '184', '185', '190', '191', '192', '200', '201', '202', '207', '208', '209', '212', '213']

# Create an MCP server instance with puzzle identifier
app = Server("my-mcp-server")

def load_puzzle_data():
    """Load puzzle data from JSON file and filter to only allowed IDs"""
    global puzzle_data
    try:
        with open(PUZZLE_DATA_PATH, 'r') as f:
            data = json.load(f)
        
        # Convert to dict format if needed
        if isinstance(data, list):
            all_puzzles = {str(i): puzzle for i, puzzle in enumerate(data)}
        else:
            all_puzzles = data
        
        # Filter to only include allowed puzzle IDs
        puzzle_data = {id: all_puzzles[id] for id in ALLOWED_PUZZLE_IDS if id in all_puzzles}
        
        logger.info(f"Loaded {len(puzzle_data)} puzzles from allowed list of {len(ALLOWED_PUZZLE_IDS)} IDs")
        logger.info(f"Available puzzle IDs: {list(puzzle_data.keys())}")
        
        # Warn about missing puzzle IDs
        missing_ids = [id for id in ALLOWED_PUZZLE_IDS if id not in all_puzzles]
        if missing_ids:
            logger.warning(f"Missing puzzle IDs from data: {missing_ids}")
            
    except Exception as e:
        logger.error(f"Failed to load puzzle data: {e}")
        puzzle_data = {}

def get_random_questions(count: int) -> list:
    """Select random questions without replacement using Fisher-Yates shuffle"""
    global puzzle_data
    
    # Get available IDs that actually exist in the loaded data
    available_ids = [id for id in ALLOWED_PUZZLE_IDS if id in puzzle_data]
    
    if not available_ids:
        raise ValueError("No puzzle data available")
    
    # Guard against requesting more than available
    take = min(count, len(available_ids))
    
    # Fisher–Yates shuffle for unbiased sampling without replacement
    ids = available_ids.copy()
    for i in range(len(ids) - 1, 0, -1):
        j = random.randint(0, i)
        ids[i], ids[j] = ids[j], ids[i]
    
    # Take the first 'take' elements
    selected_ids = ids[:take]
    
    logger.info(f"Selected {len(selected_ids)} puzzle IDs for session: {selected_ids}")
    
    return selected_ids

# Load puzzle data on startup
load_puzzle_data()

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools for the puzzle MCP server"""
    return [
        types.Tool(
            name="create_session",
            description="Create a new puzzle session",
            inputSchema={
                "type": "object",
                "required": ["session_id"],
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Unique identifier for the session"
                    },
                    "puzzle_count": {
                        "type": "integer",
                        "description": "Number of puzzles in the session",
                        "default": 5
                    },
                    "min_correct": {
                        "type": "integer", 
                        "description": "Minimum correct answers needed to complete session",
                        "default": 2
                    }
                }
            }
        ),
        types.Tool(
            name="get_session_status",
            description="Get the status of a puzzle session",
            inputSchema={
                "type": "object",
                "required": ["session_id"],
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier"
                    }
                }
            }
        ),
        types.Tool(
            name="submit_answer",
            description="Submit an answer for the current puzzle",
            inputSchema={
                "type": "object",
                "required": ["session_id", "answer"],
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier"
                    },
                    "answer": {
                        "type": "string",
                        "description": "The submitted answer"
                    }
                }
            }
        ),
        types.Tool(
            name="get_random_puzzle",
            description="Get a random puzzle from the allowed puzzle IDs",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_secret",
            description="Get the secret - only available after completing a session successfully",
            inputSchema={
                "type": "object",
                "required": ["session_id"],
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier"
                    }
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(
    name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls for the puzzle MCP server"""
    global sessions, puzzle_data
    
    if name == "create_session":
        return [types.TextContent(type="text", text=create_session_impl(**arguments))]
    elif name == "get_session_status":
        return [types.TextContent(type="text", text=get_session_status_impl(**arguments))]
    elif name == "submit_answer":
        return [types.TextContent(type="text", text=submit_answer_impl(**arguments))]
    elif name == "get_random_puzzle":
        return [types.TextContent(type="text", text=get_random_puzzle_impl())]
    elif name == "get_secret":
        return [types.TextContent(type="text", text=get_secret_impl(**arguments))]
    else:
        raise McpError(f"Unknown tool: {name}")

def create_session_impl(session_id: str, puzzle_count: int = 5, min_correct: int = 2) -> str:
    """
    Create a new puzzle session
    
    Args:
        session_id: Unique identifier for the session
        puzzle_count: Number of puzzles in the session (default: 5)
        min_correct: Minimum correct answers needed to complete session (default: 2)
    
    Returns:
        Session creation message with first puzzle
    """
    global sessions, puzzle_data
    
    if not puzzle_data:
        raise McpError("No puzzle data available")
    
    try:
        # Select random puzzles without replacement using Fisher-Yates shuffle
        puzzle_ids = get_random_questions(puzzle_count)
    except ValueError as e:
        raise McpError(str(e))
    
    session = {
        "session_id": session_id,
        "puzzle_ids": puzzle_ids,
        "current_index": 0,
        "correct_answers": 0,
        "min_correct": min_correct,
        "completed": False
    }
    
    sessions[session_id] = session
    
    current_puzzle = puzzle_data[puzzle_ids[0]]
    
    return f"Created session '{session_id}' with {len(puzzle_ids)} puzzles. Need {min_correct} correct answers.\n\n" + \
           f"Puzzle 1/{len(puzzle_ids)}:\n{current_puzzle.get('question', 'No question available')}"

def get_session_status_impl(session_id: str) -> str:
    """
    Get the status of a puzzle session
    
    Args:
        session_id: Session identifier
    
    Returns:
        Current session status including progress and current puzzle
    """
    global sessions, puzzle_data
    
    session = sessions.get(session_id)
    if not session:
        raise McpError(f"Session {session_id} not found")
    
    current_puzzle_id = session["puzzle_ids"][session["current_index"]]
    current_puzzle = puzzle_data[current_puzzle_id]
    
    return f"Session: {session_id}\n" + \
           f"Progress: {session['current_index'] + 1}/{len(session['puzzle_ids'])}\n" + \
           f"Correct answers: {session['correct_answers']}/{session['min_correct']}\n" + \
           f"Completed: {session['completed']}\n\n" + \
           f"Current puzzle:\n{current_puzzle.get('question', 'No question available')}"

def submit_answer_impl(session_id: str, answer: str) -> str:
    """
    Submit an answer for the current puzzle
    
    Args:
        session_id: Session identifier
        answer: The submitted answer
    
    Returns:
        Result of the answer submission and next puzzle or completion message
    """
    global sessions, puzzle_data
    
    session = sessions.get(session_id)
    if not session:
        raise McpError(f"Session {session_id} not found")
    
    if session["completed"]:
        return "Session already completed!"
    
    current_puzzle_id = session["puzzle_ids"][session["current_index"]]
    current_puzzle = puzzle_data[current_puzzle_id]
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
    
    # Check if minimum correct answers reached (early completion)
    if session["correct_answers"] >= session["min_correct"] and not session["completed"]:
        session["completed"] = True
        result_text += f"🎉 Excellent! You've reached {session['correct_answers']}/{session['min_correct']} correct answers!\n"
        result_text += "🔓 Session completed successfully! You can now access the secret!"
        return result_text
    
    if session["current_index"] >= len(session["puzzle_ids"]):
        # Session complete (all puzzles answered)
        session["completed"] = True
        if session["correct_answers"] >= session["min_correct"]:
            result_text += f"🎉 Session complete! You got {session['correct_answers']}/{session['min_correct']} correct!\n"
            result_text += "🔓 Session completed successfully!"
        else:
            result_text += f"Session complete. You got {session['correct_answers']}/{session['min_correct']} correct. Try again!"
    else:
        # Next puzzle
        next_puzzle_id = session["puzzle_ids"][session["current_index"]]
        next_puzzle = puzzle_data[next_puzzle_id]
        result_text += f"Next puzzle ({session['current_index'] + 1}/{len(session['puzzle_ids'])}):\n"
        result_text += next_puzzle.get('question', 'No question available')
    
    return result_text

def get_random_puzzle_impl() -> str:
    """
    Get a random puzzle from the allowed puzzle IDs
    
    Returns:
        A random puzzle with its solution
    """
    global puzzle_data
    
    if not puzzle_data:
        raise McpError("No puzzle data available")
    
    # Select from available allowed puzzle IDs
    available_ids = [id for id in ALLOWED_PUZZLE_IDS if id in puzzle_data]
    if not available_ids:
        raise McpError("No allowed puzzle IDs available")
    
    puzzle_id = random.choice(available_ids)
    puzzle = puzzle_data[puzzle_id]
    
    return f"Random Puzzle (ID: {puzzle_id}):\n\n{puzzle.get('question', 'No question available')}\n\n" + \
           f"Solution: {puzzle.get('solution', 'No solution available')}"

def get_secret_impl(session_id: str) -> str:
    """
    Get the secret - only available after completing a session successfully
    
    Args:
        session_id: Session identifier
    
    Returns:
        The secret message if session was completed successfully, otherwise puzzles to solve
    """
    global sessions
    
    session = sessions.get(session_id)
    if not session:
        # No session found, start a new one
        create_result = create_session_impl(session_id, puzzle_count=3, min_correct=2)
        return f"🔒 Secret locked! You must complete puzzles first.\n\n{create_result}"
    
    # Check if user has reached minimum correct answers (regardless of completion status)
    if session["correct_answers"] >= session["min_correct"]:
        # Session completed successfully - reveal the secret!
        return "🔓 SECRET UNLOCKED! 🔓\n\n" + \
               "🎉 Congratulations! You've proven your puzzle-solving skills!\n\n" + \
               "💎 THE SECRET: We are currently clean on OPSEC\n\n" + \
               f"✨ You completed session '{session_id}' with {session['correct_answers']}/{session['min_correct']} correct answers!"
    
    if not session["completed"]:
        # Session not completed yet and not enough correct answers
        current_puzzle_id = session["puzzle_ids"][session["current_index"]]
        current_puzzle = puzzle_data[current_puzzle_id]
        return f"🔒 Secret locked! You need {session['min_correct']} correct answers. Current: {session['correct_answers']}\n\n" + \
               f"Current puzzle ({session['current_index'] + 1}/{len(session['puzzle_ids'])}):\n" + \
               current_puzzle.get('question', 'No question available')
    else:
        # Session completed but not enough correct answers
        return f"🔒 Secret still locked! You completed the session but only got {session['correct_answers']}/{session['min_correct']} correct answers.\n\n" + \
               "Try starting a new session to unlock the secret!"

async def run_stdio_server():
    """Run the MCP server using STDIO"""
    logger.info("Starting MCP server with STDIO transport")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

def run_sse_server(host: str = "0.0.0.0", port: int = 8001):
    """Run the MCP server using SSE (Server-Sent Events)"""
    logger.info(f"Starting MCP server with SSE transport on {host}:{port}")
    
    # Create SSE transport
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        """Handle SSE requests"""
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (reader, writer):
            await app.run(reader, writer, app.create_initialization_options())

    from starlette.requests import Request
    from starlette.routing import Route
    
    async def handle_sse_endpoint(request: Request):
        """Handle SSE endpoint requests"""
        await handle_sse(request)

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse_endpoint),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )
    
    uvicorn.run(starlette_app, host=host, port=port)

def run_streamable_http_server(host: str = "0.0.0.0", port: int = 8001):
    """Run the MCP server using StreamableHTTP"""
    logger.info(f"Starting MCP server with StreamableHTTP transport on {host}:{port}")
    
    # StreamableHTTP session manager
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        stateless=True,
    )

    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
        """Handle StreamableHTTP requests"""
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(starlette_app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )
    
    uvicorn.run(starlette_app, host=host, port=port)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Puzzle MCP Server")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "http", "sse"], 
        default="http",
        help="Transport method: 'stdio' for standard input/output, 'http' for StreamableHTTP, 'sse' for Server-Sent Events (default: http)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="Host to bind to for HTTP/SSE transport (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8001,
        help="Port to bind to for HTTP/SSE transport (default: 8001)"
    )
    
    args = parser.parse_args()
    
    print(f"🧩 Starting Puzzle MCP Server")
    print(f"📊 Loaded {len(puzzle_data)} puzzles")
    print(f"🔧 Available tools: create_session, get_session_status, submit_answer, get_random_puzzle, get_secret")
    print(f"🚀 Transport: {args.transport.upper()}")
    
    if args.transport == "stdio":
        print("📡 Using STDIO transport")
        import asyncio
        asyncio.run(run_stdio_server())
    elif args.transport == "sse":
        print(f"📡 Using SSE transport on {args.host}:{args.port}")
        run_sse_server(host=args.host, port=args.port)
    else:
        print(f"📡 Using StreamableHTTP transport on {args.host}:{args.port}")
        run_streamable_http_server(host=args.host, port=args.port)