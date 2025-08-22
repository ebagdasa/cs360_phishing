# Puzzle MCP Server

This is a Model Context Protocol (MCP) server that provides access to academic puzzles from your existing puzzle database. The server allows AI assistants to interact with puzzles through standardized tools and resources.

## Features

- **Random Puzzle Access**: Get random puzzles from a curated collection
- **Puzzle Search**: Search puzzles by subject domain or keywords
- **Answer Verification**: Check if answers are correct
- **Session Management**: Create multi-puzzle sessions with progress tracking
- **Category Discovery**: List all available subject domains
- **Resource Access**: Direct access to puzzle data via URI resources

## Available Tools

### 1. `get_random_puzzle`
Get a random puzzle from the curated collection.

**Parameters:**
- `exclude_ids` (optional): Array of puzzle IDs to exclude

**Example:**
```json
{
  "exclude_ids": ["1", "154"]
}
```

### 2. `get_puzzle_by_id`
Get a specific puzzle by its ID.

**Parameters:**
- `puzzle_id` (required): The ID of the puzzle to retrieve

### 3. `check_puzzle_answer`
Check if an answer is correct for a given puzzle.

**Parameters:**
- `puzzle_id` (required): The ID of the puzzle
- `answer` (required): The answer to check

### 4. `create_puzzle_session`
Create a new puzzle session with multiple puzzles.

**Parameters:**
- `session_id` (required): Unique identifier for the session
- `puzzle_count` (optional, default: 5): Number of puzzles in the session
- `min_correct` (optional, default: 2): Minimum correct answers required

### 5. `get_session_status`
Get the current status of a puzzle session.

**Parameters:**
- `session_id` (required): The session ID

### 6. `submit_session_answer`
Submit an answer for the current puzzle in a session.

**Parameters:**
- `session_id` (required): The session ID
- `answer` (required): The answer to submit

### 7. `list_puzzle_categories`
List all unique subject domains found in puzzles.

### 8. `search_puzzles`
Search puzzles by subject domain or keywords.

**Parameters:**
- `domain` (optional): Subject domain to search for
- `keywords` (optional): Array of keywords to search for
- `limit` (optional, default: 10): Maximum number of results

## Available Resources

### `puzzle://data/all`
Complete puzzle database with all questions and solutions.

### `puzzle://data/curated`
Curated subset of puzzles used in the web interface.

## Installation

1. **Install Dependencies:**
   ```bash
   pip install mcp pydantic pydantic-settings
   ```

2. **Make the server executable:**
   ```bash
   chmod +x puzzle_mcp_server.py
   ```

## Usage

### Running the Server

The server runs using the Model Context Protocol over stdio:

```bash
python puzzle_mcp_server.py
```

### Configuration for MCP Clients

Add this to your MCP client configuration:

```json
{
  "mcpServers": {
    "puzzle-server": {
      "command": "python",
      "args": ["puzzle_mcp_server.py"],
      "cwd": "/path/to/your/puzzle/directory"
    }
  }
}
```

### Testing

Run the test script to verify everything works:

```bash
python test_puzzle_server.py
```

## Example Usage

### Getting a Random Puzzle
```python
# Through MCP client
result = await client.call_tool("get_random_puzzle", {})
puzzle = json.loads(result[0].text)
print(f"Puzzle: {puzzle['question']}")
```

### Creating a Puzzle Session
```python
# Create a session with 5 puzzles, need 3 correct to win
result = await client.call_tool("create_puzzle_session", {
    "session_id": "my_session",
    "puzzle_count": 5,
    "min_correct": 3
})

session = json.loads(result[0].text)
print(f"First puzzle: {session['current_puzzle']['question']}")
```

### Submitting Answers
```python
# Submit an answer to the current puzzle in the session
result = await client.call_tool("submit_session_answer", {
    "session_id": "my_session",
    "answer": "your_answer"
})

response = json.loads(result[0].text)
if response['answer_correct']:
    print("Correct!")
if response['secret_revealed']:
    print(f"Secret message: {response['secret_message']}")
```

## Puzzle Data Structure

Each puzzle contains:
- `question`: The puzzle text with interdisciplinary clues
- `solution`: The correct answer (lowercase)
- `generator response`: Additional metadata from the puzzle generation process

## Curated Puzzle IDs

The server uses a curated list of puzzle IDs that have been tested and verified:
['1', '154', '157', '159', '165', '171', '173', '174', '178', '180', '182', '184', '185', '190', '191', '192', '200', '201', '202', '207', '208', '209', '212', '213']

## Error Handling

The server provides detailed error messages for:
- Invalid puzzle IDs
- Missing sessions
- Completed sessions
- Invalid tool parameters

## Logging

The server logs important events including:
- Puzzle data loading
- Tool call errors
- Session operations

Set the logging level in the script to control verbosity:
```python
logging.basicConfig(level=logging.DEBUG)  # For more detailed logs
```

## Integration with Claude Desktop

To use this MCP server with Claude Desktop, add the configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "puzzle-server": {
      "command": "python",
      "args": ["/path/to/puzzle_mcp_server.py"],
      "cwd": "/path/to/puzzle/directory"
    }
  }
}
```

Then restart Claude Desktop, and you'll be able to ask Claude to interact with your puzzles using natural language!

## Files Created

- `puzzle_mcp_server.py` - Main MCP server implementation
- `test_puzzle_server.py` - Test script for verification
- `mcp_config.json` - Example MCP configuration
- `requirements.txt` - Python dependencies
- `README.md` - This documentation file
