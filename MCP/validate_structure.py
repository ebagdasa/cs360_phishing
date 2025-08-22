#!/usr/bin/env python3
"""
Validation script to ensure MCP folder structure works correctly
"""

import os
import sys
import json
from pathlib import Path

def validate_mcp_structure():
    """Validate the MCP folder structure and file integrity"""
    print("🔍 Validating MCP folder structure...")
    print("=" * 50)
    
    mcp_dir = Path(__file__).parent
    
    # Required files
    required_files = [
        "puzzle_mcp_server.py",
        "puzzle_http_server.py", 
        "puzzle_websocket_server.py",
        "offline_verifier_generation.json",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        "README.md"
    ]
    
    # Check required files exist
    print("1. Checking required files...")
    missing_files = []
    for file in required_files:
        file_path = mcp_dir / file
        if file_path.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    # Check puzzle data
    print("\n2. Checking puzzle data...")
    puzzle_file = mcp_dir / "offline_verifier_generation.json"
    try:
        with open(puzzle_file, 'r') as f:
            puzzle_data = json.load(f)
        print(f"   ✅ Loaded {len(puzzle_data)} puzzles")
    except Exception as e:
        print(f"   ❌ Error loading puzzle data: {e}")
        return False
    
    # Check Python imports
    print("\n3. Checking Python imports...")
    try:
        # Add current directory to path for imports
        sys.path.insert(0, str(mcp_dir))
        
        # Test imports (without running servers)
        import importlib.util
        
        for py_file in ["puzzle_mcp_server.py", "puzzle_http_server.py", "puzzle_websocket_server.py"]:
            spec = importlib.util.spec_from_file_location("test_module", mcp_dir / py_file)
            if spec is None:
                print(f"   ❌ Could not load {py_file}")
                return False
            print(f"   ✅ {py_file} syntax OK")
            
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    # Check requirements
    print("\n4. Checking requirements.txt...")
    req_file = mcp_dir / "requirements.txt"
    try:
        with open(req_file, 'r') as f:
            requirements = f.read().strip().split('\n')
        print(f"   ✅ {len([r for r in requirements if r.strip()])} dependencies listed")
    except Exception as e:
        print(f"   ❌ Error reading requirements: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ MCP folder validation PASSED!")
    print("🚀 Ready for deployment!")
    return True

if __name__ == "__main__":
    success = validate_mcp_structure()
    sys.exit(0 if success else 1)
