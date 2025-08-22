#!/usr/bin/env python3
"""
Test script for HTTP deployment of Puzzle MCP Server
"""

import asyncio
import httpx
import json
import sys

async def test_http_server(base_url="http://127.0.0.1:8000"):
    """Test the HTTP server functionality"""
    print(f"🌐 Testing Puzzle HTTP Server at {base_url}")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Health check
            print("1. Testing health endpoint...")
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ Health check passed: {health_data['puzzles_loaded']} puzzles loaded")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
            
            # Test 2: Get random puzzle
            print("\n2. Testing random puzzle endpoint...")
            response = await client.get(f"{base_url}/api/puzzles/random")
            if response.status_code == 200:
                puzzle_data = response.json()
                print(f"   ✅ Random puzzle: ID {puzzle_data['puzzle_id']}")
                print(f"   📝 Solution: {puzzle_data['solution']}")
            else:
                print(f"   ❌ Random puzzle failed: {response.status_code}")
                return False
            
            # Test 3: Create session
            print("\n3. Testing session creation...")
            session_data = {
                "session_id": "http_test_session",
                "puzzle_count": 3,
                "min_correct": 2
            }
            response = await client.post(f"{base_url}/api/sessions", json=session_data)
            if response.status_code == 200:
                session_response = response.json()
                print(f"   ✅ Session created: {session_response['total_puzzles']} puzzles")
                session_id = session_response['session_id']
            else:
                print(f"   ❌ Session creation failed: {response.status_code}")
                return False
            
            # Test 4: Get session status
            print("\n4. Testing session status...")
            response = await client.get(f"{base_url}/api/sessions/{session_id}")
            if response.status_code == 200:
                status_data = response.json()
                print(f"   ✅ Session status: Question {status_data['current_question']}/{status_data['total_questions']}")
                current_puzzle_id = status_data['current_puzzle']['puzzle_id']
            else:
                print(f"   ❌ Session status failed: {response.status_code}")
                return False
            
            # Test 5: Submit answer (get correct answer first)
            print("\n5. Testing answer submission...")
            # Get the correct answer for testing
            puzzle_response = await client.get(f"{base_url}/api/puzzles/{current_puzzle_id}")
            if puzzle_response.status_code == 200:
                puzzle_detail = puzzle_response.json()
                correct_answer = puzzle_detail['solution']
                
                # Submit the correct answer
                answer_data = {
                    "session_id": session_id,
                    "answer": correct_answer
                }
                response = await client.post(f"{base_url}/api/sessions/{session_id}/answer", json=answer_data)
                if response.status_code == 200:
                    answer_response = response.json()
                    print(f"   ✅ Answer submitted: {'Correct' if answer_response['answer_correct'] else 'Incorrect'}")
                    print(f"   📊 Score: {answer_response['correct_answers']}/{session_data['min_correct']}")
                    
                    if answer_response.get('secret_revealed'):
                        print(f"   🎉 Secret revealed: {answer_response.get('secret_message', 'N/A')}")
                else:
                    print(f"   ❌ Answer submission failed: {response.status_code}")
                    return False
            else:
                print(f"   ❌ Getting puzzle details failed: {puzzle_response.status_code}")
                return False
            
            # Test 6: API documentation
            print("\n6. Testing API documentation...")
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print(f"   ✅ API docs accessible at {base_url}/docs")
            else:
                print(f"   ⚠️  API docs not accessible (this is normal for some deployments)")
            
            print("\n" + "=" * 50)
            print("✅ All HTTP server tests passed!")
            print(f"🌐 Server ready for external agents at {base_url}")
            return True
            
        except httpx.ConnectError:
            print(f"❌ Could not connect to server at {base_url}")
            print("   Make sure the server is running with:")
            print("   python puzzle_http_server.py --host 0.0.0.0 --port 8000")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

async def main():
    """Main test function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://127.0.0.1:8000"
    
    success = await test_http_server(base_url)
    
    if success:
        print("\n🎯 HTTP deployment test PASSED!")
        print("Your server is ready for remote agent connections!")
    else:
        print("\n💻 HTTP deployment test FAILED!")
        print("Please check server configuration and try again.")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted")
        sys.exit(1)
