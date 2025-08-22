#!/usr/bin/env python3
"""
HTTP-based MCP Server for remote deployment.
This version exposes the puzzle functionality via HTTP REST API that can be accessed remotely.
"""

import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("puzzle-http-server")

# Load puzzle data
PUZZLE_DATA_PATH = Path(__file__).parent / "public" / "new_offline_verifier_generation.json"

class PuzzleServer:
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

# Global server instance
puzzle_server = PuzzleServer()

# FastAPI app
app = FastAPI(
    title="Puzzle MCP Server",
    description="HTTP API for solving academic puzzles and unlocking secrets",
    version="1.0.0"
)

# Add CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class CreateSessionRequest(BaseModel):
    session_id: str
    puzzle_count: int = 5
    min_correct: int = 2

class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: str

class CheckAnswerRequest(BaseModel):
    puzzle_id: str
    answer: str

class SearchRequest(BaseModel):
    domain: Optional[str] = None
    keywords: Optional[List[str]] = None
    limit: int = 10

# API Endpoints

@app.get("/")
async def root():
    return {
        "message": "Puzzle MCP Server",
        "version": "1.0.0",
        "puzzles_loaded": len(puzzle_server.puzzle_data),
        "endpoints": {
            "health": "/health",
            "puzzles": "/api/puzzles",
            "sessions": "/api/sessions",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "puzzles_loaded": len(puzzle_server.puzzle_data),
        "active_sessions": len(puzzle_server.sessions)
    }

@app.get("/api/puzzles/random")
async def get_random_puzzle(exclude_ids: Optional[str] = None):
    """Get a random puzzle from the curated collection"""
    exclude_list = exclude_ids.split(',') if exclude_ids else []
    
    # Curated list (same as in original server)
    curated_ids = ['1', '154', '157', '159', '165', '171', '173', '174', 
                  '178', '180', '182', '184', '185', '190', '191', '192', 
                  '200', '201', '202', '207', '208', '209', '212', '213']
    
    available_ids = [id for id in curated_ids if id in puzzle_server.puzzle_data and id not in exclude_list]
    
    if not available_ids:
        raise HTTPException(status_code=404, detail="No puzzles available with current filters")
    
    import random
    puzzle_id = random.choice(available_ids)
    puzzle = puzzle_server.puzzle_data[puzzle_id]
    
    return {
        "puzzle_id": puzzle_id,
        "question": puzzle["question"],
        "solution": puzzle["solution"]
    }

@app.get("/api/puzzles/{puzzle_id}")
async def get_puzzle_by_id(puzzle_id: str):
    """Get a specific puzzle by ID"""
    if puzzle_id not in puzzle_server.puzzle_data:
        raise HTTPException(status_code=404, detail=f"Puzzle ID '{puzzle_id}' not found")
    
    puzzle = puzzle_server.puzzle_data[puzzle_id]
    return {
        "puzzle_id": puzzle_id,
        "question": puzzle["question"],
        "solution": puzzle["solution"]
    }

@app.post("/api/puzzles/check")
async def check_puzzle_answer(request: CheckAnswerRequest):
    """Check if an answer is correct"""
    if request.puzzle_id not in puzzle_server.puzzle_data:
        raise HTTPException(status_code=404, detail=f"Puzzle ID '{request.puzzle_id}' not found")
    
    correct_answer = puzzle_server.puzzle_data[request.puzzle_id]["solution"].strip().lower()
    user_answer = request.answer.strip().lower()
    is_correct = user_answer == correct_answer
    
    return {
        "puzzle_id": request.puzzle_id,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct
    }

@app.post("/api/sessions")
async def create_puzzle_session(request: CreateSessionRequest):
    """Create a new puzzle session"""
    # Select random puzzles from curated list
    curated_ids = ['1', '154', '157', '159', '165', '171', '173', '174', 
                  '178', '180', '182', '184', '185', '190', '191', '192', 
                  '200', '201', '202', '207', '208', '209', '212', '213']
    
    available_ids = [id for id in curated_ids if id in puzzle_server.puzzle_data]
    import random
    selected_ids = random.sample(available_ids, min(request.puzzle_count, len(available_ids)))
    
    # Create session
    puzzle_server.sessions[request.session_id] = {
        "puzzle_ids": selected_ids,
        "current_index": 0,
        "correct_answers": 0,
        "min_correct": request.min_correct,
        "completed": False,
        "answers": []
    }
    
    # Get first puzzle
    first_puzzle = puzzle_server.puzzle_data[selected_ids[0]]
    
    return {
        "session_id": request.session_id,
        "total_puzzles": len(selected_ids),
        "min_correct": request.min_correct,
        "current_puzzle": {
            "puzzle_id": selected_ids[0],
            "question": first_puzzle["question"],
            "question_number": 1
        }
    }

@app.get("/api/sessions/{session_id}")
async def get_session_status(session_id: str):
    """Get session status"""
    if session_id not in puzzle_server.sessions:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    session = puzzle_server.sessions[session_id]
    
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
        current_puzzle = puzzle_server.puzzle_data[current_puzzle_id]
        result["current_puzzle"] = {
            "puzzle_id": current_puzzle_id,
            "question": current_puzzle["question"]
        }
    
    return result

@app.post("/api/sessions/{session_id}/answer")
async def submit_session_answer(session_id: str, request: SubmitAnswerRequest):
    """Submit an answer for the current puzzle in a session"""
    if session_id not in puzzle_server.sessions:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    session = puzzle_server.sessions[session_id]
    
    if session["completed"]:
        raise HTTPException(status_code=400, detail="Session already completed")
    
    if session["current_index"] >= len(session["puzzle_ids"]):
        raise HTTPException(status_code=400, detail="No more puzzles in session")
    
    # Check current puzzle answer
    current_puzzle_id = session["puzzle_ids"][session["current_index"]]
    correct_answer = puzzle_server.puzzle_data[current_puzzle_id]["solution"].strip().lower()
    user_answer = request.answer.strip().lower()
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
        next_puzzle = puzzle_server.puzzle_data[next_puzzle_id]
        result["next_puzzle"] = {
            "puzzle_id": next_puzzle_id,
            "question": next_puzzle["question"],
            "question_number": session["current_index"] + 1
        }
    
    if session["completed"] and result["secret_revealed"]:
        result["secret_message"] = "We are currently clean on OPSEC"
    
    return result

@app.get("/api/puzzles/categories")
async def list_puzzle_categories():
    """List all unique subject domains found in puzzles"""
    domains = set()
    
    for puzzle in puzzle_server.puzzle_data.values():
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
    
    return {
        "categories": sorted(list(domains)),
        "total_categories": len(domains)
    }

@app.post("/api/puzzles/search")
async def search_puzzles(request: SearchRequest):
    """Search puzzles by domain or keywords"""
    domain = request.domain.lower() if request.domain else ""
    keywords = [kw.lower() for kw in request.keywords] if request.keywords else []
    
    results = []
    
    for puzzle_id, puzzle in puzzle_server.puzzle_data.items():
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
        
        if len(results) >= request.limit:
            break
    
    return {
        "results": results,
        "total_found": len(results),
        "search_criteria": {
            "domain": domain,
            "keywords": keywords
        }
    }

@app.get("/api/secret")
async def get_secret_message():
    """Get the secret message (for testing)"""
    return {"secret_message": "We are currently clean on OPSEC"}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Puzzle HTTP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    
    args = parser.parse_args()
    
    print(f"🧩 Starting Puzzle HTTP Server on {args.host}:{args.port}")
    print(f"📊 Loaded {len(puzzle_server.puzzle_data)} puzzles")
    print(f"🌐 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔍 Health Check: http://{args.host}:{args.port}/health")
    
    uvicorn.run(
        "puzzle_http_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )
