# Puzzle MCP Server

A Model Context Protocol (MCP) server that provides puzzle-solving tools with session management and secret unlocking functionality. The server uses a curated set of 24 puzzles with sampling without replacement.

## Features

The server provides the following MCP tools:

### Available Tools

1. **`create_session`** - Create a new puzzle session
   - Parameters:
     - `session_id` (string): Unique identifier for the session
     - `puzzle_count` (int, optional): Number of puzzles (default: 5)
     - `min_correct` (int, optional): Minimum correct answers needed (default: 3)

2. **`get_session_status`** - Get current session status
   - Parameters:
     - `session_id` (string): Session identifier
   - Returns: Progress, current puzzle, and session details

3. **`submit_answer`** - Submit an answer for the current puzzle
   - Parameters:
     - `session_id` (string): Session identifier
     - `answer` (string): Your answer to the current puzzle
   - Returns: Result feedback and next puzzle or completion message

4. **`get_random_puzzle`** - Get a random puzzle with solution
   - No parameters required
   - Returns: A random puzzle from the curated list (includes solution)

5. **`get_secret`** - Unlock the secret (requires completed session)
   - Parameters:
     - `session_id` (string): Session identifier
   - Returns: Either puzzle challenges or the secret if session completed successfully

## Puzzle Selection

The server uses a curated list of 24 high-quality puzzle IDs:
`['1', '154', '157', '159', '165', '171', '173', '174', '178', '180', '182', '184', '185', '190', '191', '192', '200', '201', '202', '207', '208', '209', '212', '213']`

### Sampling Strategy

- **Without Replacement**: Each session uses Fisher-Yates shuffle to ensure no duplicate puzzles
- **Graceful Handling**: Requesting more puzzles than available returns all available puzzles
- **Consistent Quality**: Only vetted puzzle IDs are used (same as Express server)

## How to Use

### Starting the Server

```bash
cd MCP/
python mcp_server.py
```

The server will start on `localhost:8001` with SSE (Server-Sent Events) transport.

### Example Usage Flow

1. **Create a session:**
   ```python
   create_session("my_session", puzzle_count=3, min_correct=2)
   ```

2. **Check status:**
   ```python
   get_session_status("my_session")
   ```

3. **Submit answers:**
   ```python
   submit_answer("my_session", "your_answer_here")
   ```

4. **Unlock the secret** (after completing session successfully):
   ```python
   get_secret("my_session")
   ```

### Secret Unlocking

The `get_secret` tool implements a progressive challenge system:

- If no session exists, it creates one automatically
- If session exists but isn't completed, it shows the current puzzle
- If session is completed with enough correct answers, it reveals the secret: **"We are currently clean on OPSEC"**
- If session is completed but with insufficient correct answers, it prompts to try again

## Technical Details

- **Framework**: Uses `mcp.server.fastmcp.FastMCP`
- **Transport**: SSE (Server-Sent Events) for VS Code integration
- **Data**: Loads puzzles from `offline_verifier_generation.json` (filtered to 24 specific IDs)
- **Session Management**: In-memory storage for active puzzle sessions
- **Error Handling**: Proper MCP error responses with appropriate error codes
- **Sampling**: Fisher-Yates shuffle for unbiased sampling without replacement

## Testing

Run the test scripts to verify functionality:

```bash
# Test all tools
python test_mcp_puzzle_tools.py

# Test secret unlock flow
python test_updated_secret.py

# Test puzzle filtering and sampling
python test_filtered_puzzles.py
```

## Integration

This MCP server can be integrated with VS Code using the MCP extension. Configure it to connect to `http://localhost:8001` with SSE transport.

The server follows the MCP protocol and can be used with any MCP-compatible client.
