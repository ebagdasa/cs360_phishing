#!/usr/bin/env python3
"""
Test script to verify the updated secret message
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from mcp_server import create_session, get_session_status, submit_answer, get_secret, puzzle_data

def test_updated_secret():
    """Test the updated secret message"""
    print("🧪 Testing Updated Secret Message\n")
    
    # Create a session with 2 puzzles, need 1 correct
    print("1. Creating session...")
    result = create_session("secret_test_new", puzzle_count=2, min_correct=1)
    print(f"✅ Session created: {result[:100]}...\n")
    
    # Get the current session to find puzzle IDs
    from mcp_server import sessions
    session = sessions["secret_test_new"]
    
    print("2. Completing session to unlock secret...")
    
    # Submit correct answer for first puzzle
    puzzle_id = session["puzzle_ids"][0]
    correct_answer = puzzle_data[puzzle_id]["solution"]
    print(f"Submitting correct answer for puzzle {puzzle_id}: '{correct_answer}'")
    
    result = submit_answer("secret_test_new", correct_answer)
    print(f"✅ First answer submitted: {result[:100]}...\n")
    
    # Submit any answer for second puzzle (we only need 1 correct out of 2)
    result = submit_answer("secret_test_new", "any_answer")
    print(f"✅ Second answer submitted: {result[:100]}...\n")
    
    # Now try to get the secret
    print("3. Unlocking the secret...")
    result = get_secret("secret_test_new")
    print(f"🔓 SECRET RESULT:\n{result}\n")
    
    # Check if the new secret message is present
    expected_secret = "We are currently clean on OPSEC"
    if expected_secret in result:
        print("🎉 SUCCESS! The correct secret message was revealed!")
        print(f"✅ Found expected secret: '{expected_secret}'")
    else:
        print("❌ ERROR: Expected secret message not found!")
        print(f"❌ Expected: '{expected_secret}'")
        print(f"❌ Got: {result}")
    
    if "SECRET UNLOCKED" in result:
        print("✅ Secret unlock formatting is correct!")
    else:
        print("❌ Secret unlock formatting is missing!")
    
    print("\n" + "="*50)
    print("Secret message test completed!")

if __name__ == "__main__":
    test_updated_secret()
