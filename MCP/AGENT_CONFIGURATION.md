# External Agent Configuration for Puzzle MCP Server

This guide explains how to configure external agents to connect to the Puzzle MCP Server and solve puzzles to unlock the secret message.

## 🎯 Mission for External Agents

**Objective**: Connect to the Puzzle MCP Server, solve academic puzzles, and unlock the secret message.

**Success Criteria**: 
- Get at least 2 correct answers out of 5 puzzles (configurable)
- Unlock the secret message: "We are currently clean on OPSEC"

## 🚀 Quick Start

### 1. Start the MCP Server

```bash
cd /Users/ebagdasnryan/Documents/development/random/openai_assistant

# Method 1: Direct execution
python puzzle_mcp_server.py

# Method 2: With conda environment
/opt/miniconda3/bin/conda run -p /opt/miniconda3 --no-capture-output python puzzle_mcp_server.py
```

The server will run on stdio and wait for MCP client connections.

### 2. Verify Server Functionality

Before connecting external agents, test the server:

```bash
# Test core logic
python test_server_logic.py

# Test example agent (demonstrates solving approach)
python example_external_agent.py
```

### 2. Agent Configuration

#### For Claude Desktop
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "puzzle-server": {
      "command": "python",
      "args": ["/Users/ebagdasnryan/Documents/development/random/openai_assistant/puzzle_mcp_server.py"],
      "cwd": "/Users/ebagdasnryan/Documents/development/random/openai_assistant"
    }
  }
}
```

#### For Other MCP Clients
Use the MCP client library to connect via stdio:
```python
import subprocess
import json

# Start the server process
process = subprocess.Popen(
    ["python", "puzzle_mcp_server.py"],
    cwd="/Users/ebagdasnryan/Documents/development/random/openai_assistant",
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
```

#### For OpenAI Assistants API
If using OpenAI's Assistants with custom tools, configure the server endpoint and use HTTP calls to interact with the tools.

#### For LangChain/LangSmith Agents
```python
from langchain.tools import Tool
from mcp_client import MCPClient

client = MCPClient("puzzle_mcp_server.py")
tools = client.get_tools()
```

## 🛠️ Available Tools for Agents

### Core Puzzle Tools

#### 1. `create_puzzle_session` - Start a New Challenge
**Purpose**: Create a multi-puzzle session with configurable difficulty
```json
{
  "name": "create_puzzle_session",
  "arguments": {
    "session_id": "agent_session_001",
    "puzzle_count": 5,
    "min_correct": 2
  }
}
```

#### 2. `get_session_status` - Check Progress
**Purpose**: Get current session state and next puzzle
```json
{
  "name": "get_session_status",
  "arguments": {
    "session_id": "agent_session_001"
  }
}
```

#### 3. `submit_session_answer` - Submit Solutions
**Purpose**: Submit answers and progress through the session
```json
{
  "name": "submit_session_answer",
  "arguments": {
    "session_id": "agent_session_001",
    "answer": "your_answer_here"
  }
}
```

### Helper Tools

#### 4. `get_random_puzzle` - Practice Mode
```json
{
  "name": "get_random_puzzle",
  "arguments": {
    "exclude_ids": ["1", "154"]
  }
}
```

#### 5. `check_puzzle_answer` - Verify Solutions
```json
{
  "name": "check_puzzle_answer",
  "arguments": {
    "puzzle_id": "185",
    "answer": "pearl"
  }
}
```

#### 6. `search_puzzles` - Find Specific Types
```json
{
  "name": "search_puzzles",
  "arguments": {
    "domain": "computer science",
    "limit": 3
  }
}
```

#### 7. `list_puzzle_categories` - Explore Domains
```json
{
  "name": "list_puzzle_categories",
  "arguments": {}
}
```

## 🎮 Agent Strategy Guide

### Recommended Workflow

1. **Initialize Session**
   ```
   create_puzzle_session(session_id="unique_id", puzzle_count=5, min_correct=2)
   ```

2. **Main Game Loop**
   ```
   while not completed:
       status = get_session_status(session_id)
       current_puzzle = status.current_puzzle.question
       
       # Agent analyzes puzzle and determines answer
       answer = solve_puzzle(current_puzzle)
       
       result = submit_session_answer(session_id, answer)
       
       if result.secret_revealed:
           secret = result.secret_message
           break
   ```

3. **Puzzle Solving Approach**
   - Puzzles are interdisciplinary with clues from multiple academic domains
   - Extract the first letter of answers to form words
   - Common domains: computer science, mathematics, physics, biology, chemistry, etc.
   - Answers are always lowercase

### Example Puzzle Format
```
begin your journey by deciphering these interdisciplinary clues. for each clue, 
determine the answer and then record the initial letter of that answer. the 
sequentially extracted letters will reveal the hidden word.

• humanities subdomain 45: consider the ancient epic that recounts the legendary 
  siege of troy—identify its title and record the first letter.
• social science subdomain 53: in the study of societal organization, uncover the 
  term that describes the layering of social classes and extract its starting letter.
...

solution = isles (i-s-l-e-s from: Iliad, Stratification, Line, Ethnography, Sociology)
```

## 📊 Success Metrics

### Session Response Format
```json
{
  "session_id": "agent_session_001",
  "answer_correct": true,
  "correct_answers": 2,
  "completed": false,
  "secret_revealed": true,
  "secret_message": "We are currently clean on OPSEC",
  "next_puzzle": {
    "puzzle_id": "173",
    "question": "...",
    "question_number": 3
  }
}
```

### Victory Conditions
- `secret_revealed: true` - Agent has reached minimum correct answers
- `secret_message: "We are currently clean on OPSEC"` - The target secret
- `completed: true` - All puzzles in session finished

## 🐛 Troubleshooting

### Common Issues

1. **Server Not Starting**
   ```bash
   # Check dependencies
   pip install mcp pydantic pydantic-settings
   
   # Verify puzzle data exists
   ls public/new_offline_verifier_generation.json
   ```

2. **Connection Issues**
   ```bash
   # Test server logic
   python test_server_logic.py
   ```

3. **Puzzle Loading Errors**
   - Ensure `new_offline_verifier_generation.json` is in the `public/` directory
   - Check file permissions and encoding (should be UTF-8)

### Debug Mode
Enable detailed logging in the server:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🧪 Testing Your Agent

### Verification Steps

1. **Test Basic Connection**
   ```python
   # Your agent should be able to call:
   tools = client.list_tools()
   assert "create_puzzle_session" in [t.name for t in tools]
   ```

2. **Test Session Creation**
   ```python
   result = client.call_tool("create_puzzle_session", {
       "session_id": "test",
       "puzzle_count": 1,
       "min_correct": 1
   })
   assert "total_puzzles" in result
   ```

3. **Test Answer Submission**
   ```python
   # Get the correct answer first
   status = client.call_tool("get_session_status", {"session_id": "test"})
   puzzle_id = status["current_puzzle"]["puzzle_id"]
   
   # Look up correct answer (for testing)
   puzzle = client.call_tool("get_puzzle_by_id", {"puzzle_id": puzzle_id})
   correct_answer = puzzle["solution"]
   
   # Submit and verify
   result = client.call_tool("submit_session_answer", {
       "session_id": "test",
       "answer": correct_answer
   })
   assert result["answer_correct"] == True
   ```

## 📈 Performance Tips

- **Parallel Processing**: You can run multiple sessions simultaneously
- **Caching**: Store puzzle solutions for faster subsequent runs
- **Domain Knowledge**: Build knowledge bases for each academic domain
- **Pattern Recognition**: Many puzzles follow similar formats

## 🎯 Agent Success Examples

### Sample Agent Pseudocode
```python
class PuzzleSolvingAgent:
    def __init__(self, mcp_client):
        self.client = mcp_client
        self.domain_knowledge = load_academic_knowledge()
    
    async def solve_session(self):
        session_id = f"agent_{random.randint(1000, 9999)}"
        
        # Create session
        await self.client.call_tool("create_puzzle_session", {
            "session_id": session_id,
            "puzzle_count": 5,
            "min_correct": 2
        })
        
        while True:
            status = await self.client.call_tool("get_session_status", {
                "session_id": session_id
            })
            
            if status.get("completed") or status.get("secret_revealed"):
                return status.get("secret_message")
            
            puzzle = status["current_puzzle"]["question"]
            answer = self.solve_puzzle(puzzle)
            
            result = await self.client.call_tool("submit_session_answer", {
                "session_id": session_id,
                "answer": answer
            })
            
            if result.get("secret_revealed"):
                return result.get("secret_message")
    
    def solve_puzzle(self, puzzle_text):
        # Extract clues and solve each one
        clues = self.extract_clues(puzzle_text)
        letters = []
        
        for clue in clues:
            answer = self.solve_clue(clue)
            letters.append(answer[0].lower())
        
        return ''.join(letters)
```

---

## 🏆 Mission Complete

When your agent successfully unlocks the secret message "We are currently clean on OPSEC", it has demonstrated:

- ✅ MCP protocol integration
- ✅ Multi-domain academic knowledge
- ✅ Sequential reasoning and puzzle solving
- ✅ Session state management
- ✅ Goal-oriented problem solving

Good luck with your agent! 🚀
