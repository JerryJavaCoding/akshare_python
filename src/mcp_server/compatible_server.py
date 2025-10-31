"""MCP Server with compatibility for older MCP clients."""
import asyncio
import json
import sys
from typing import Any, Dict, List

from .finance_tools import FinanceDataService


class MCPCompatibleServer:
    """MCP Server compatible with older MCP protocol versions."""
    
    def __init__(self):
        self.tools = self._get_tools()
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools."""
        return [
            {
                "name": "echo",
                "description": "Echo back the input text",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to echo back"
                        }
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "calculate",
                "description": "Perform basic arithmetic calculations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "get_time",
                "description": "Get current time information",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_stock_spot",
                "description": "获取股票实时行情数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码（如：000001），为空则返回所有股票"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_stock_history",
                "description": "获取股票历史数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码（如：000001）",
                        },
                        "period": {
                            "type": "string",
                            "description": "数据周期：daily(日线), weekly(周线), monthly(月线)",
                            "enum": ["daily", "weekly", "monthly"]
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_fund_info",
                "description": "获取基金信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "基金代码"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_index_data",
                "description": "获取指数数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "指数代码（如：000001 上证指数），为空则返回主要指数"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_futures_data",
                "description": "获取期货数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "期货代码，为空则返回主要期货"
                        }
                    },
                    "required": []
                }
            }
        ]
    
    async def handle_list_tools(self) -> Dict[str, Any]:
        """Handle mcp:list-tools request."""
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": self.tools
            }
        }
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution."""
        try:
            if name == "echo":
                if not arguments or "text" not in arguments:
                    raise ValueError("Missing 'text' argument")
                return {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": arguments["text"]
                            }
                        ]
                    }
                }
            
            elif name == "calculate":
                if not arguments or "expression" not in arguments:
                    raise ValueError("Missing 'expression' argument")
                try:
                    # Basic safe evaluation
                    result = eval(arguments["expression"], {"__builtins__": {}})
                    return {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Result: {result}"
                                }
                            ]
                        }
                    }
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Error: {str(e)}"
                                }
                            ]
                        }
                    }
            
            elif name == "get_time":
                import datetime
                current_time = datetime.datetime.now()
                return {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                }
            
            # Finance tools
            elif name == "get_stock_spot":
                symbol = arguments.get("symbol", "") if arguments else ""
                result = FinanceDataService.get_stock_spot(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_stock_history":
                if not arguments or "symbol" not in arguments:
                    raise ValueError("Missing 'symbol' argument")
                symbol = arguments["symbol"]
                period = arguments.get("period", "daily")
                result = FinanceDataService.get_stock_history(symbol, period)
                return {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_fund_info":
                if not arguments or "symbol" not in arguments:
                    raise ValueError("Missing 'symbol' argument")
                symbol = arguments["symbol"]
                result = FinanceDataService.get_fund_info(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_index_data":
                symbol = arguments.get("symbol", "") if arguments else ""
                result = FinanceDataService.get_index_data(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_futures_data":
                symbol = arguments.get("symbol", "") if arguments else ""
                result = FinanceDataService.get_futures_data(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            else:
                raise ValueError(f"Unknown tool: {name}")
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }
    
    async def handle_initialize(self) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": "2024-11-01",
                "capabilities": {},
                "serverInfo": {
                    "name": "python-finance-server",
                    "version": "1.0.0"
                }
            }
        }
    
    async def process_message(self, message: str) -> str:
        """Process incoming JSON-RPC message."""
        try:
            data = json.loads(message)
            method = data.get("method", "")
            params = data.get("params", {})
            
            if method == "initialize":
                result = await self.handle_initialize()
            elif method == "mcp:list-tools":
                result = await self.handle_list_tools()
            elif method == "mcp:call-tool":
                tool_name = params.get("name", "")
                tool_args = params.get("arguments", {})
                result = await self.handle_call_tool(tool_name, tool_args)
            else:
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            return json.dumps(result)
            
        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            })


async def main():
    """Main server loop."""
    server = MCPCompatibleServer()
    
    # Read from stdin, write to stdout
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            line = line.strip()
            if line:
                response = await server.process_message(line)
                print(response, flush=True)
                
        except Exception as e:
            error_response = json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            })
            print(error_response, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
