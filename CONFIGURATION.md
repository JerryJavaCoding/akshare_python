# MCP客户端配置指南

本文档详细说明如何在不同MCP客户端中配置和连接Python MCP服务器。

## 支持的MCP客户端

### 1. Claude Desktop

Claude Desktop是最常用的MCP客户端之一。

#### 配置步骤：

1. **找到配置文件位置**：
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **编辑配置文件**：
```json
{
  "mcpServers": {
    "python-finance-server": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "/path/to/your/mcp-python-project"
    }
  }
}
```

3. **重启Claude Desktop**应用

#### 完整配置示例：
```json
{
  "mcpServers": {
    "python-finance-server": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "/Users/jerry/code/akshare_python",
      "env": {
        "PYTHONPATH": "/Users/jerry/code/akshare_python/src"
      }
    }
  }
}
```

### 2. Cline (当前环境)

在Cline环境中，MCP服务器会自动被发现和使用。您可以直接运行：

```bash
python -m src.mcp_server.server
```

### 3. 其他MCP客户端

#### 通用配置格式：
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

## 环境要求

### Python环境
确保您的Python环境已安装所有依赖：
```bash
# 在项目目录中执行
pip install -e .
```

### 验证安装
```bash
python -c "import akshare; print('akshare installed successfully')"
python -c "import mcp; print('MCP installed successfully')"
```

## 故障排除

### 常见问题

1. **"Command not found: python"**
   - 解决方案：使用完整Python路径
   ```json
   "command": "/usr/bin/python3"
   ```

2. **ModuleNotFoundError**
   - 解决方案：确保`cwd`指向正确目录
   - 检查PYTHONPATH环境变量

3. **权限问题**
   - 解决方案：确保Python脚本有执行权限

### 调试模式

要调试MCP服务器，可以添加环境变量：
```json
{
  "mcpServers": {
    "finance-data": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "/path/to/project",
      "env": {
        "MCP_DEBUG": "1"
      }
    }
  }
}
```

## 使用示例

配置成功后，您可以在客户端中直接使用金融数据工具：

```
请帮我获取上证指数的实时数据
```

客户端会自动调用`get_index_data`工具并返回结果。

## 安全注意事项

1. **网络访问**：akshare需要网络连接获取实时数据
2. **数据源**：数据来自公开的金融数据接口
3. **使用限制**：请遵守相关数据使用条款
