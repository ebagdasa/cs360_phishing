#!/usr/bin/env python3
"""
Test script for the puzzle MCP server.
This script demonstrates how to interact with the puzzle server programmatically.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

from puzzle_mcp_server import PuzzleServer

async def test_puzzle_server():
    """Test the puzzle server functionality"""
    print("🧩 Testing Puzzle MCP Server")
    print("=" * 50)
    
    # Create server instance
    server = PuzzleServer()
    
    # Test 1: Get a random puzzle
    print("\n1. Testing get_random_puzzle:")
    result = await server.get_random_puzzle({})
    puzzle_data = json.loads(result[0].text)
    print(f"   Got puzzle ID: {puzzle_data['puzzle_id']}")
    print(f"   Question preview: {puzzle_data['question'][:100]}...")
    
    # Test 2: Get puzzle by ID
    print("\n2. Testing get_puzzle_by_id:")
    result = await server.get_puzzle_by_id({"puzzle_id": "1"})
    puzzle_data = json.loads(result[0].text)
    print(f"   Retrieved puzzle ID: {puzzle_data['puzzle_id']}")
    print(f"   Solution: {puzzle_data['solution']}")
    
    # Test 3: Check answer
    print("\n3. Testing check_puzzle_answer:")
    result = await server.check_puzzle_answer({
        "puzzle_id": "1", 
        "answer": "isles"
    })
    check_data = json.loads(result[0].text)
    print(f"   Answer 'isles' is correct: {check_data['is_correct']}")
    
    # Test 4: Create puzzle session
    print("\n4. Testing create_puzzle_session:")
    result = await server.create_puzzle_session({
        "session_id": "test_session_123",
        "puzzle_count": 3,
        "min_correct": 2
    })
    session_data = json.loads(result[0].text)
    print(f"   Created session with {session_data['total_puzzles']} puzzles")
    print(f"   First puzzle ID: {session_data['current_puzzle']['puzzle_id']}")
    
    # Test 5: Submit answer to session
    print("\n5. Testing submit_session_answer:")
    result = await server.submit_session_answer({
        "session_id": "test_session_123",
        "answer": "wrong_answer"
    })
    answer_data = json.loads(result[0].text)
    print(f"   Answer was correct: {answer_data['answer_correct']}")
    print(f"   Session completed: {answer_data['completed']}")
    
    # Test 6: List puzzle categories
    print("\n6. Testing list_puzzle_categories:")
    result = await server.list_puzzle_categories({})
    categories_data = json.loads(result[0].text)
    print(f"   Found {categories_data['total_categories']} categories")
    print(f"   Sample categories: {categories_data['categories'][:5]}")
    
    # Test 7: Search puzzles
    print("\n7. Testing search_puzzles:")
    result = await server.search_puzzles({
        "domain": "computer science",
        "limit": 2
    })
    search_data = json.loads(result[0].text)
    print(f"   Found {search_data['total_found']} computer science puzzles")
    
    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_puzzle_server())
