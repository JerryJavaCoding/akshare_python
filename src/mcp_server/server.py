"""MCP Server implementation."""
import asyncio
from typing import Any
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from .finance_tools import FinanceDataService, FINANCE_TOOLS

# Create server instance
server = Server("python-mcp-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="echo",
            description="Echo back the input text",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to echo back"
                    }
                },
                "required": ["text"]
            }
        ),
        types.Tool(
            name="calculate",
            description="Perform basic arithmetic calculations",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        ),
        types.Tool(
            name="get_time",
            description="Get current time information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        *FINANCE_TOOLS  # Add all finance tools
    ]


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution."""
    if name == "echo":
        if not arguments or "text" not in arguments:
            raise ValueError("Missing 'text' argument")
        return [types.TextContent(type="text", text=arguments["text"])]
    
    elif name == "calculate":
        if not arguments or "expression" not in arguments:
            raise ValueError("Missing 'expression' argument")
        try:
            # Basic safe evaluation (in production, use a safer approach)
            result = eval(arguments["expression"], {"__builtins__": {}})
            return [types.TextContent(type="text", text=f"Result: {result}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "get_time":
        import datetime
        current_time = datetime.datetime.now()
        return [types.TextContent(
            type="text", 
            text=f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )]
    
    # Finance tools
    elif name == "get_stock_spot":
        symbol = arguments.get("symbol", "") if arguments else ""
        return FinanceDataService.get_stock_spot(symbol)
    
    elif name == "get_stock_history":
        if not arguments or "symbol" not in arguments:
            raise ValueError("Missing 'symbol' argument")
        symbol = arguments["symbol"]
        period = arguments.get("period", "daily")
        return FinanceDataService.get_stock_history(symbol, period)
    
    elif name == "get_fund_info":
        if not arguments or "symbol" not in arguments:
            raise ValueError("Missing 'symbol' argument")
        symbol = arguments["symbol"]
        return FinanceDataService.get_fund_info(symbol)
    
    elif name == "get_index_data":
        symbol = arguments.get("symbol", "") if arguments else ""
        return FinanceDataService.get_index_data(symbol)
    
    elif name == "get_futures_data":
        symbol = arguments.get("symbol", "") if arguments else ""
        return FinanceDataService.get_futures_data(symbol)
    
    else:
        raise ValueError(f"Unknown tool: {name}")


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources."""
    return [
        types.Resource(
            uri="example://info",
            name="Example Information",
            description="Example resource providing basic information",
            mimeType="text/plain"
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read resource content."""
    if uri == "example://info":
        return "This is an example resource from the Python MCP server."
    else:
        raise ValueError(f"Unknown resource: {uri}")


async def main():
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="python-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=mcp.server.NotificationOptions(
                        resources_changed=False
                    ),
                    experimental_capabilities=None,
                )
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
