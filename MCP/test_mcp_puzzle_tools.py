#!/usr/bin/env python3
"""
Test script for the MCP puzzle tools
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from mcp_server import create_session, get_session_status, submit_answer, get_random_puzzle, get_secret

def test_puzzle_tools():
    """Test all the puzzle tools"""
    print("🧪 Testing MCP Puzzle Tools\n")
    
    # Test 1: Create a session
    print("1. Testing create_session...")
    try:
        result = create_session("test_session_1", puzzle_count=3, min_correct=2)
        print("✅ create_session works!")
        print(f"Result: {result[:100]}...\n")
    except Exception as e:
        print(f"❌ create_session failed: {e}\n")
        return
    
    # Test 2: Get session status
    print("2. Testing get_session_status...")
    try:
        result = get_session_status("test_session_1")
        print("✅ get_session_status works!")
        print(f"Result: {result[:100]}...\n")
    except Exception as e:
        print(f"❌ get_session_status failed: {e}\n")
        return
    
    # Test 3: Submit a wrong answer
    print("3. Testing submit_answer (wrong answer)...")
    try:
        result = submit_answer("test_session_1", "wrong_answer")
        print("✅ submit_answer works!")
        print(f"Result: {result[:100]}...\n")
    except Exception as e:
        print(f"❌ submit_answer failed: {e}\n")
        return
    
    # Test 4: Get random puzzle
    print("4. Testing get_random_puzzle...")
    try:
        result = get_random_puzzle()
        print("✅ get_random_puzzle works!")
        print(f"Result: {result[:100]}...\n")
    except Exception as e:
        print(f"❌ get_random_puzzle failed: {e}\n")
        return
    
    # Test 5: Get secret (should be locked)
    print("5. Testing get_secret (should be locked)...")
    try:
        result = get_secret("test_session_1")
        print("✅ get_secret works!")
        print(f"Result: {result[:100]}...\n")
    except Exception as e:
        print(f"❌ get_secret failed: {e}\n")
        return
    
    # Test 6: Test secret with non-existent session
    print("6. Testing get_secret with new session...")
    try:
        result = get_secret("new_session_for_secret")
        print("✅ get_secret with new session works!")
        print(f"Result: {result[:100]}...\n")
    except Exception as e:
        print(f"❌ get_secret with new session failed: {e}\n")
        return
    
    print("🎉 All tests passed!")

if __name__ == "__main__":
    test_puzzle_tools()
