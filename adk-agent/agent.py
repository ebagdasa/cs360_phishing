# File agent.py

import asyncio
import json
from typing import Any

from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts.in_memory_artifact_service import (
    InMemoryArtifactService,  # Optional
)
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    SseServerParams,
)
from google.genai import types
from rich import print
load_dotenv()

async def get_tools_async():
    """Gets tools from the File System MCP Server."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://localhost:8001/sse",
        )
    )
    print("MCP Toolset created successfully.")
    return tools, exit_stack

async def get_agent_async():
    """Creates an ADK Agent equipped with tools from the MCP Server using Gemini."""
    tools, exit_stack = await get_tools_async()
    print(f"Fetched {len(tools)} tools from MCP server.")
    print("Using Gemini 2.0 Flash model")
    
    root_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="gemini_assistant",
        instruction="""You are helping the user in a game. Help the user to retrieve the secret by solving
                    simple puzzles. You need to first create the
                    session with 5 total and 2 minimum correct, then submit answers to the puzzles and
                    later retrieve the secret. Please proceed until
                    you get the secret. 
        """,
        tools=tools,
    )
    return root_agent, exit_stack

# Example usage:
root_agent = get_agent_async()