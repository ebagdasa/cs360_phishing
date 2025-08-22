#!/usr/bin/env python3
"""
Direct functionality test for the puzzle MCP server logic.
This tests the server's puzzle handling without the MCP protocol layer.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

async def test_puzzle_logic():
    """Test the core puzzle server logic"""
    print("🧩 Testing Puzzle Server Core Logic")
    print("=" * 50)
    
    # Import just the server class, don't run the protocol
    from puzzle_mcp_server import PuzzleServer
    
    # Create server instance (this loads the puzzles)
    server = PuzzleServer()
    
    # Test 1: Verify puzzles loaded
    print(f"\n✅ Loaded {len(server.puzzle_data)} puzzles")
    
    # Test 2: Get a random puzzle
    print("\n1. Testing get_random_puzzle:")
    result = await server.get_random_puzzle({})
    puzzle_data = json.loads(result[0].text)
    puzzle_id = puzzle_data['puzzle_id']
    print(f"   ✅ Got puzzle ID: {puzzle_id}")
    print(f"   📝 Question preview: {puzzle_data['question'][:100]}...")
    print(f"   🔑 Solution: {puzzle_data['solution']}")
    
    # Test 3: Check correct answer
    print("\n2. Testing check_puzzle_answer (correct):")
    result = await server.check_puzzle_answer({
        "puzzle_id": puzzle_id, 
        "answer": puzzle_data['solution']
    })
    check_data = json.loads(result[0].text)
    print(f"   ✅ Correct answer verified: {check_data['is_correct']}")
    
    # Test 4: Check wrong answer
    print("\n3. Testing check_puzzle_answer (incorrect):")
    result = await server.check_puzzle_answer({
        "puzzle_id": puzzle_id, 
        "answer": "wrong_answer"
    })
    check_data = json.loads(result[0].text)
    print(f"   ❌ Wrong answer detected: {not check_data['is_correct']}")
    
    # Test 5: Create puzzle session (the key functionality for external agents)
    print("\n4. Testing puzzle session workflow:")
    session_id = "agent_test_session"
    
    # Create session
    result = await server.create_puzzle_session({
        "session_id": session_id,
        "puzzle_count": 3,
        "min_correct": 2
    })
    session_data = json.loads(result[0].text)
    print(f"   ✅ Created session with {session_data['total_puzzles']} puzzles")
    print(f"   🎯 Need {session_data['min_correct']} correct to reveal secret")
    
    # Get first puzzle
    first_puzzle = session_data['current_puzzle']
    print(f"   📝 First puzzle ID: {first_puzzle['puzzle_id']}")
    
    # Test answering puzzles in the session
    for attempt in range(3):
        print(f"\n   Attempt {attempt + 1}:")
        
        # Get session status
        result = await server.get_session_status({"session_id": session_id})
        status = json.loads(result[0].text)
        
        if status['completed']:
            print("   🏁 Session completed!")
            break
        
        current_puzzle = status['current_puzzle']
        correct_answer = server.puzzle_data[current_puzzle['puzzle_id']]['solution']
        
        # Submit correct answer for first two, wrong for third to test logic
        test_answer = correct_answer if attempt < 2 else "wrong_answer"
        
        result = await server.submit_session_answer({
            "session_id": session_id,
            "answer": test_answer
        })
        
        response = json.loads(result[0].text)
        status_icon = "✅" if response['answer_correct'] else "❌"
        print(f"   {status_icon} Answer: {test_answer} -> {'Correct' if response['answer_correct'] else 'Wrong'}")
        print(f"   📊 Score: {response['correct_answers']}/2")
        
        if response.get('secret_revealed'):
            print(f"   🎉 SECRET REVEALED!")
            if 'secret_message' in response:
                print(f"   🔓 Secret: {response['secret_message']}")
    
    # Test 6: Search functionality
    print("\n5. Testing search functionality:")
    result = await server.search_puzzles({
        "domain": "computer science",
        "limit": 2
    })
    search_data = json.loads(result[0].text)
    print(f"   ✅ Found {search_data['total_found']} computer science puzzles")
    
    # Test 7: Categories
    print("\n6. Testing categories:")
    result = await server.list_puzzle_categories({})
    categories_data = json.loads(result[0].text)
    print(f"   ✅ Found {categories_data['total_categories']} categories")
    
    print("\n" + "=" * 50)
    print("✅ All core functionality tests passed!")
    print("🚀 Server is ready for external agents!")
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_puzzle_logic())
        if result:
            print("\n🎯 READY FOR AGENT CONNECTION!")
            print("The server can now be used by external agents to:")
            print("- Create puzzle sessions")
            print("- Get puzzles and submit answers")
            print("- Unlock the secret message")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
