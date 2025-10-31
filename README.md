# Python MCP Server

A Python implementation of a Model Context Protocol (MCP) server.

## Overview

This project provides a Python-based MCP server with example tools and resources that can be used with MCP-compatible clients.

## Features

- **Basic Tools**:
  - `echo`: Echo back the input text
  - `calculate`: Perform basic arithmetic calculations
  - `get_time`: Get current time information

- **Financial Data Tools (using akshare)**:
  - `get_stock_spot`: 获取股票实时行情数据
  - `get_stock_history`: 获取股票历史数据
  - `get_fund_info`: 获取基金信息
  - `get_index_data`: 获取指数数据
  - `get_futures_data`: 获取期货数据

- **Resources**:
  - `example://info`: Example resource providing basic information

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd mcp-python-project
```

2. Install dependencies:
```bash
pip install -e .
```

For development dependencies:
```bash
pip install -e ".[dev]"
```

## Usage

### Running the Server

You can run the server directly:

```bash
python -m src.mcp_server.server
```

### MCP客户端连接配置

#### Claude Desktop 配置

编辑配置文件 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "python-finance-server": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "/Users/jerry/code/akshare_python"
    }
  }
}
```

#### 其他MCP客户端

通用配置格式：
```json
{
  "mcpServers": {
    "finance-data": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "/absolute/path/to/your/project"
    }
  }
}
```

详细配置说明请参考 [CONFIGURATION.md](CONFIGURATION.md)。

## Development

### Project Structure

```
mcp-python-project/
├── src/
│   └── mcp_server/
│       ├── __init__.py
│       ├── server.py
│       └── finance_tools.py
├── scripts/
│   └── run_server.py
├── tests/
│   └── test_server.py
├── pyproject.toml
├── README.md
└── .gitignore
```

### Financial Data Examples

The server provides access to various financial data through akshare:

```python
# Get real-time stock data
get_stock_spot(symbol="000001")

# Get historical stock data
get_stock_history(symbol="000001", period="daily")

# Get fund information
get_fund_info(symbol="000001")

# Get index data
get_index_data(symbol="000001")

# Get futures data
get_futures_data(symbol="AU0")
```

### Adding New Tools

To add a new tool:

1. Add the tool definition in `handle_list_tools()`
2. Implement the tool logic in `handle_call_tool()`

Example:

```python
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        # ... existing tools ...
        types.Tool(
            name="new_tool",
            description="Description of the new tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter description"}
                },
                "required": ["param"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None):
    if name == "new_tool":
        # Implement tool logic here
        return [types.TextContent(type="text", text="Tool result")]
```

### Adding New Resources

To add a new resource:

1. Add the resource definition in `handle_list_resources()`
2. Implement the resource reading logic in `handle_read_resource()`

## Testing

Run tests with:

```bash
pytest
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
