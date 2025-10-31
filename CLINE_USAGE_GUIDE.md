# Cline 使用 MCP 工具指南

## 在 Cline 中配置 MCP 服务器

### 方法一：通过环境变量配置

在启动 Cline 之前设置环境变量：

```bash
export MCP_SERVERS='{
  "python-finance-server": {
    "command": "python",
    "args": ["/Users/jerry/code/akshare_python/scripts/run_compatible_server.py"]
  }
}'
```

然后启动 Cline，MCP 工具会自动加载。

### 方法二：在 Cline 配置文件中配置

如果 Cline 支持配置文件，可以编辑 Cline 的配置文件：

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

### 方法三：在 Cline 会话中直接使用

由于您当前就在 Cline 环境中，可以直接运行 MCP 服务器并使用工具：

```bash
# 启动 MCP 服务器（后台运行）
python scripts/run_compatible_server.py &
```

## 在 Cline 中使用 MCP 工具

### 基础工具使用

1. **回显文本**
   ```
   请使用 echo 工具回显 "Hello World"
   ```

2. **数学计算**
   ```
   请计算 2+3*4 的结果
   ```

3. **获取时间**
   ```
   请告诉我当前时间
   ```

### 金融数据工具使用

1. **获取股票实时行情**
   ```
   请获取股票 000001 的实时行情数据
   ```

2. **获取股票历史数据**
   ```
   请获取股票 000001 的历史数据，周期为日线
   ```

3. **获取基金信息**
   ```
   请获取基金 000001 的信息
   ```

4. **获取指数数据**
   ```
   请获取上证指数的实时数据
   ```

5. **获取期货数据**
   ```
   请获取黄金期货的数据
   ```

## 完整使用示例

### 示例 1：股票数据分析
```
请帮我分析股票 000001：
1. 获取实时行情
2. 获取最近的历史数据
3. 计算涨跌幅
```

### 示例 2：投资组合分析
```
请帮我创建一个简单的投资组合分析：
1. 获取上证指数数据
2. 获取几只主要股票的实时行情
3. 计算整体表现
```

### 示例 3：金融计算
```
请帮我计算：
1. 计算 10000 元投资，年化收益率 8%，5 年后的价值
2. 获取当前时间
3. 回显计算结果
```

## 故障排除

### 如果工具不可用

1. **检查服务器状态**
   ```bash
   python scripts/run_compatible_server.py
   ```

2. **验证依赖**
   ```bash
   pip install -e .
   ```

3. **重启 Cline 会话**

### 调试模式

如果需要调试，可以启用调试模式：
```bash
export MCP_DEBUG=1
python scripts/run_compatible_server.py
```

## 可用的工具列表

### 基础工具
- `echo` - 回显输入文本
- `calculate` - 执行数学计算
- `get_time` - 获取当前时间

### 金融数据工具
- `get_stock_spot` - 获取股票实时行情
- `get_stock_history` - 获取股票历史数据
- `get_fund_info` - 获取基金信息
- `get_index_data` - 获取指数数据
- `get_futures_data` - 获取期货数据

## 最佳实践

1. **明确指定工具**：在请求中明确说明要使用的工具
2. **提供完整参数**：确保提供工具所需的所有必要参数
3. **组合使用**：可以组合多个工具完成复杂任务
4. **错误处理**：如果某个工具失败，尝试使用其他替代方案

## 实时使用示例

现在您可以直接在 Cline 中尝试：

```
请帮我获取上证指数的实时数据，并计算今天的涨跌幅
```

Cline 会自动调用相应的 MCP 工具并返回结果。
