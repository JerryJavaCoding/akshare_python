#!/usr/bin/env python3
"""Script to run the finance MCP server with all integrated tools."""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.mcp_server.finance_server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
