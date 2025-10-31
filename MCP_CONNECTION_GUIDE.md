# MCP客户端连接指南

## 当前服务器状态
- **服务器位置**: `/Users/jerry/code/akshare_python`
- **启动命令**: `python -m src.mcp_server.server`
- **服务器状态**: 已启动并运行

## CherryStudio 连接配置（兼容版本）

### 方法一：配置文件方式（推荐）

1. **找到配置文件**：
   ```bash
   # macOS
   open ~/Library/Application\ Support/CherryStudio/config.json
   ```

2. **编辑配置文件**，添加以下内容：
   ```json
   {
     "mcpServers": {
       "python-finance-server": {
         "command": "python",
         "args": ["/Users/jerry/code/akshare_python/scripts/run_compatible_server.py"]
       }
     }
   }
   ```

3. **完整配置文件示例**：
   ```json
   {
     "mcpServers": {
       "python-finance-server": {
         "command": "python",
         "args": ["/Users/jerry/code/akshare_python/scripts/run_compatible_server.py"]
       }
     }
   }
   ```

### 方法二：环境变量方式

在终端中设置环境变量，然后启动CherryStudio：
```bash
export MCP_SERVERS='{
  "python-finance-server": {
    "command": "python",
    "args": ["/Users/jerry/code/akshare_python/scripts/run_compatible_server.py"]
  }
}'
# 然后启动 CherryStudio
```

### 方法三：界面配置

1. 打开 CherryStudio
2. 进入设置 → MCP Servers
3. 添加新服务器：
   - **Name**: `python-finance-server`
   - **Command**: `python`
   - **Arguments**: `/Users/jerry/code/akshare_python/scripts/run_compatible_server.py`

## 验证连接

### 步骤1：确认服务器运行
```bash
cd /Users/jerry/code/akshare_python
python -m src.mcp_server.server
```
如果看到服务器启动成功，说明服务正常。

### 步骤2：在CherryStudio中测试
配置完成后重启CherryStudio，然后尝试使用以下命令：
- "echo 测试连接"
- "get_time"
- "get_stock_spot symbol=000001"

## 其他MCP客户端配置

### Claude Desktop
编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：
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

### 通用配置格式
```json
{
  "mcpServers": {
    "finance-data": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "/Users/jerry/code/akshare_python"
    }
  }
}
```

## 故障排除

### 常见问题

1. **连接失败**
   - 检查服务器是否正在运行
   - 验证Python路径是否正确
   - 确保所有依赖已安装：`pip install -e .`

2. **工具不可用**
   - 重启CherryStudio
   - 检查MCP服务器日志
   - 验证配置文件格式

3. **权限问题**
   - 确保Python脚本有执行权限
   - 检查文件路径权限

### 调试模式
如需调试，可以添加环境变量：
```json
{
  "mcpServers": {
    "python-finance-server": {
      "command": "python",
      "args": ["/Users/jerry/code/akshare_python/scripts/run_server.py"],
      "env": {
        "MCP_DEBUG": "1"
      }
    }
  }
}
```

## 可用的工具列表

配置成功后，您可以使用以下工具：

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

## 使用示例

在CherryStudio中直接输入：
- "请帮我获取上证指数的实时数据"
- "计算一下 2+3*4 的结果"
- "获取股票000001的历史数据"

系统会自动调用相应的MCP工具并返回结果。
