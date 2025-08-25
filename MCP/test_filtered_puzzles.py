#!/usr/bin/env python3
"""
Test script to verify the filtered puzzle IDs and sampling without replacement
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from mcp_server import create_session, get_session_status, submit_answer, get_secret, puzzle_data, ALLOWED_PUZZLE_IDS, get_random_questions

def test_filtered_puzzles():
    """Test that only allowed puzzle IDs are used and sampling works correctly"""
    print("🧪 Testing Filtered Puzzle IDs and Sampling\n")
    
    # Test 1: Verify only allowed puzzles are loaded
    print("1. Testing puzzle filtering...")
    print(f"Total allowed puzzle IDs: {len(ALLOWED_PUZZLE_IDS)}")
    print(f"Loaded puzzle count: {len(puzzle_data)}")
    print(f"Loaded puzzle IDs: {list(puzzle_data.keys())}")
    
    # Verify all loaded IDs are in the allowed list
    for puzzle_id in puzzle_data.keys():
        if puzzle_id not in ALLOWED_PUZZLE_IDS:
            print(f"❌ ERROR: Puzzle ID {puzzle_id} is not in allowed list!")
            return
        else:
            print(f"✅ Puzzle ID {puzzle_id} is correctly in allowed list")
    
    print("✅ All loaded puzzles are from the allowed list!\n")
    
    # Test 2: Test sampling without replacement
    print("2. Testing sampling without replacement...")
    
    # Test with count equal to available puzzles
    sampled_ids = get_random_questions(5)
    print(f"Sampled 5 puzzle IDs: {sampled_ids}")
    
    # Check for duplicates
    if len(sampled_ids) != len(set(sampled_ids)):
        print("❌ ERROR: Duplicate IDs found in sampling!")
        return
    else:
        print("✅ No duplicates in sampling!")
    
    # Test with count larger than available (should handle gracefully)
    try:
        large_sample = get_random_questions(50)  # More than the 24 available
        print(f"Large sample request (50) returned {len(large_sample)} IDs: {large_sample}")
        if len(large_sample) <= len(ALLOWED_PUZZLE_IDS):
            print("✅ Large sample request handled correctly!")
        else:
            print("❌ ERROR: Large sample returned more IDs than available!")
    except Exception as e:
        print(f"❌ ERROR in large sample request: {e}")
    
    print("\n3. Testing session creation with filtered puzzles...")
    
    # Create a session and verify it uses only allowed IDs
    result = create_session("filter_test", puzzle_count=3, min_correct=2)
    print(f"Session created: {result[:100]}...")
    
    # Check the session's puzzle IDs
    from mcp_server import sessions
    session = sessions["filter_test"]
    session_puzzle_ids = session["puzzle_ids"]
    
    print(f"Session puzzle IDs: {session_puzzle_ids}")
    
    # Verify all session puzzle IDs are in allowed list
    for puzzle_id in session_puzzle_ids:
        if puzzle_id not in ALLOWED_PUZZLE_IDS:
            print(f"❌ ERROR: Session contains non-allowed puzzle ID {puzzle_id}!")
            return
        else:
            print(f"✅ Session puzzle ID {puzzle_id} is in allowed list")
    
    # Check for duplicates in session
    if len(session_puzzle_ids) != len(set(session_puzzle_ids)):
        print("❌ ERROR: Session contains duplicate puzzle IDs!")
        return
    else:
        print("✅ No duplicates in session puzzle IDs!")
    
    print("\n🎉 All filtering and sampling tests passed!")

if __name__ == "__main__":
    test_filtered_puzzles()
