# CherryStudio MCP 配置指南

## CherryStudio 中连接本地 MCP 服务

### 方法一：通过环境变量配置

在 CherryStudio 中，通常可以通过环境变量或配置文件来添加 MCP 服务器。

#### 1. 设置环境变量
```bash
export MCP_SERVERS='{
  "python-finance-server": {
    "command": "python",
    "args": ["-m", "src.mcp_server.server"],
    "cwd": "/Users/jerry/code/akshare_python"
  }
}'
```

#### 2. 在 CherryStudio 启动脚本中添加
如果 CherryStudio 有启动脚本，可以在其中添加：
```bash
#!/bin/bash
export MCP_SERVERS='{
  "python-finance-server": {
    "command": "python", 
    "args": ["-m", "src.mcp_server.server"],
    "cwd": "/Users/jerry/code/akshare_python"
  }
}'
# 启动 CherryStudio
/path/to/cherrystudio
```

### 方法二：通过配置文件

#### 1. 查找 CherryStudio 配置文件
CherryStudio 的配置文件通常位于：
- macOS: `~/Library/Application Support/CherryStudio/config.json`
- Linux: `~/.config/CherryStudio/config.json`
- Windows: `%APPDATA%\CherryStudio\config.json`

#### 2. 编辑配置文件（修正版本）
由于CherryStudio不支持`cwd`参数，请使用以下配置：

**方案一：使用绝对路径**
```json
{
  "mcpServers": {
    "python-finance-server": {
      "command": "python",
      "args": ["/Users/jerry/code/akshare_python/scripts/run_server.py"]
    }
  }
}
```

**方案二：使用环境变量设置工作目录**
```json
{
  "mcpServers": {
    "python-finance-server": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "env": {
        "PYTHONPATH": "/Users/jerry/code/akshare_python/src"
      }
    }
  }
}
```

**方案三：使用完整路径运行模块**
```json
{
  "mcpServers": {
    "python-finance-server": {
      "command": "python",
      "args": ["-c", "import sys; sys.path.insert(0, '/Users/jerry/code/akshare_python'); from src.mcp_server.server import main; import asyncio; asyncio.run(main())"]
    }
  }
}
```

### 方法三：通过命令行参数

如果 CherryStudio 支持命令行参数启动 MCP 服务器：
```bash
cherrystudio --mcp-server python-finance-server:python:-m:src.mcp_server.server:/Users/jerry/code/akshare_python
```

### 方法四：在 CherryStudio 界面中配置

1. 打开 CherryStudio
2. 进入设置或偏好设置
3. 查找 "MCP Servers" 或 "External Tools" 选项
4. 添加新的 MCP 服务器：
   - Name: `python-finance-server`
   - Command: `python`
   - Arguments: `-m src.mcp_server.server`
   - Working Directory: `/Users/jerry/code/akshare_python`

### 验证配置

#### 1. 首先测试 MCP 服务器是否能正常运行
```bash
cd /Users/jerry/code/akshare_python
python -m src.mcp_server.server
```

如果看到服务器启动成功，说明 MCP 服务正常。

#### 2. 在 CherryStudio 中测试连接
配置完成后，在 CherryStudio 中尝试使用 MCP 工具：
- 输入 "获取上证指数数据"
- 或使用具体的工具调用

### 故障排除

#### 1. 如果连接失败
- 检查 Python 路径是否正确
- 确保所有依赖已安装：`pip install -e .`
- 验证工作目录路径是否正确

#### 2. 如果工具不可用
- 重启 CherryStudio
- 检查 MCP 服务器是否正在运行
- 查看 CherryStudio 的日志输出

#### 3. 调试模式
可以添加环境变量来启用调试：
```json
{
  "mcpServers": {
    "python-finance-server": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "/Users/jerry/code/akshare_python",
      "env": {
        "MCP_DEBUG": "1"
      }
    }
  }
}
```

### 完整的配置示例

**推荐配置（无cwd参数）**：
```json
{
  "mcpServers": {
    "python-finance-server": {
      "command": "python",
      "args": ["/Users/jerry/code/akshare_python/scripts/run_server.py"]
    }
  }
}
```

**备选配置**：
```json
{
  "mcpServers": {
    "python-finance-server": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "env": {
        "PYTHONPATH": "/Users/jerry/code/akshare_python/src"
      }
    }
  }
}
```

### 可用的工具列表

配置成功后，您可以在 CherryStudio 中使用以下工具：

**基础工具**:
- `echo` - 回显输入文本
- `calculate` - 执行数学计算
- `get_time` - 获取当前时间

**金融数据工具**:
- `get_stock_spot` - 获取股票实时行情
- `get_stock_history` - 获取股票历史数据
- `get_fund_info` - 获取基金信息  
- `get_index_data` - 获取指数数据
- `get_futures_data` - 获取期货数据

### 使用示例

在 CherryStudio 中直接输入：
- "请帮我获取上证指数的实时数据"
- "计算一下 2+3*4 的结果"
- "获取股票000001的历史数据"

CherryStudio 会自动调用相应的 MCP 工具并返回结果。
