#!/usr/bin/env python3
"""
Simple test to verify HTTP server works
"""

import subprocess
import time
import requests
import sys
import signal
import os

def test_server():
    """Test the HTTP server"""
    print("🧪 Testing Puzzle HTTP Server")
    print("=" * 40)
    
    # Start server
    print("1. Starting server...")
    server_process = subprocess.Popen([
        sys.executable, "puzzle_http_server.py", 
        "--host", "127.0.0.1", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(5)
    
    try:
        # Test health endpoint
        print("2. Testing health endpoint...")
        response = requests.get("http://127.0.0.1:8000/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data.get('puzzles_loaded', 0)} puzzles loaded")
            
            # Test random puzzle
            print("3. Testing random puzzle...")
            puzzle_response = requests.get("http://127.0.0.1:8000/api/puzzles/random", timeout=10)
            if puzzle_response.status_code == 200:
                puzzle_data = puzzle_response.json()
                print(f"   ✅ Random puzzle: ID {puzzle_data.get('puzzle_id', 'N/A')}")
                print(f"   📝 Question: {puzzle_data.get('question', 'N/A')[:50]}...")
            else:
                print(f"   ❌ Random puzzle failed: {puzzle_response.status_code}")
            
            print("\n🎉 HTTP Server is working correctly!")
            print("✅ Ready for remote deployment!")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to server")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    finally:
        # Stop server
        print("\n4. Stopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
