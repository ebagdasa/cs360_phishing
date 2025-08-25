#!/usr/bin/env python3
"""
Test script to verify both server modes work correctly
"""

import subprocess
import time
import sys
import signal
import os

def test_sse_mode():
    """Test the server in SSE mode"""
    print("🧪 Testing SSE mode...")
    
    # Start server in SSE mode
    process = subprocess.Popen(
        [sys.executable, "mcp_server.py", "--transport", "sse", "--port", "8004"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it time to start
    time.sleep(3)
    
    # Check if process is running
    if process.poll() is None:
        print("✅ SSE server started successfully on port 8004")
        
        # Terminate the process
        process.terminate()
        try:
            process.wait(timeout=5)
            print("✅ SSE server stopped successfully")
        except subprocess.TimeoutExpired:
            process.kill()
            print("⚠️  SSE server force killed")
        
        return True
    else:
        stdout, stderr = process.communicate()
        print(f"❌ SSE server failed to start")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False

def test_http_mode():
    """Test the server in HTTP mode"""
    print("🧪 Testing HTTP mode...")
    
    # Start server in HTTP mode
    process = subprocess.Popen(
        [sys.executable, "mcp_server.py", "--transport", "http", "--port", "8003"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it time to start
    time.sleep(3)
    
    # Check if process is running
    if process.poll() is None:
        print("✅ HTTP server started successfully on port 8003")
        
        # Terminate the process
        process.terminate()
        try:
            process.wait(timeout=5)
            print("✅ HTTP server stopped successfully")
        except subprocess.TimeoutExpired:
            process.kill()
            print("⚠️  HTTP server force killed")
        
        return True
    else:
        stdout, stderr = process.communicate()
        print(f"❌ HTTP server failed to start")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False

def test_stdio_mode():
    """Test the server in STDIO mode"""
    print("🧪 Testing STDIO mode...")
    
    # Start server in STDIO mode
    process = subprocess.Popen(
        [sys.executable, "mcp_server.py", "--transport", "stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it time to start
    time.sleep(2)
    
    # Check if process is running
    if process.poll() is None:
        print("✅ STDIO server started successfully")
        
        # Terminate the process
        process.terminate()
        try:
            process.wait(timeout=5)
            print("✅ STDIO server stopped successfully")
        except subprocess.TimeoutExpired:
            process.kill()
            print("⚠️  STDIO server force killed")
        
        return True
    else:
        stdout, stderr = process.communicate()
        print(f"❌ STDIO server failed to start")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False

def main():
    print("🧩 Testing MCP Server Configuration Modes")
    print("=" * 50)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    http_success = test_http_mode()
    print()
    sse_success = test_sse_mode()
    print()
    stdio_success = test_stdio_mode()
    
    print()
    print("=" * 50)
    if http_success and sse_success and stdio_success:
        print("🎉 All tests passed! HTTP, SSE, and STDIO modes work correctly.")
    else:
        print("❌ Some tests failed. Check the output above.")
        if not http_success:
            print("   - HTTP mode failed")
        if not sse_success:
            print("   - SSE mode failed")
        if not stdio_success:
            print("   - STDIO mode failed")

if __name__ == "__main__":
    main()
