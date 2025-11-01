# akshare_python - 金融数据 MCP 服务器

基于 Python 和 akshare 库的 Model Context Protocol (MCP) 服务器，提供全面的金融数据服务。

## 功能特性

### 基础工具
- `echo`: 回显输入文本
- `calculate`: 基础数学计算
- `get_time`: 获取当前时间信息

### 股票数据服务
- `get_stock_spot`: 获取股票实时行情数据
- `get_stock_history`: 获取股票历史数据（日线/周线/月线）
- `get_stock_financials`: 获取股票财务数据
- `get_stock_valuation`: 获取股票估值数据
- `get_stock_technical_indicators`: 获取股票技术指标
- `get_stock_capital_flow`: 获取股票资金流向数据
- `get_stock_analyst_ratings`: 获取分析师评级数据
- `get_stock_company_info`: 获取公司基本信息

### 基金数据服务
- `get_fund_info`: 获取基金信息

### 指数数据服务
- `get_index_data`: 获取指数数据

### 期货数据服务
- `get_futures_data`: 获取期货数据

### 行业分析服务
- `get_industry_news`: 获取指定行业的新闻资讯
- `get_policy_support`: 获取行业政策支持信息
- `get_investment_events`: 获取投资发展重大事项
- `get_market_heat`: 获取市场热度分析
- `get_industry_overview`: 获取行业综合概览报告

## 快速开始

### 安装依赖

```bash
pip install -e .
```

开发环境安装：
```bash
pip install -e ".[dev]"
```

### 运行服务器

```bash
python scripts/run_finance_server.py
```

或直接运行模块：

```bash
python -m src.mcp_server.finance_server
```

## MCP 客户端配置

### Claude Desktop 配置

编辑配置文件 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "python-finance-server": {
      "command": "python",
      "args": ["scripts/run_finance_server.py"],
      "cwd": "/Users/jerry/code/akshare_python"
    }
  }
}
```

### 其他 MCP 客户端

通用配置格式：
```json
{
  "mcpServers": {
    "finance-data": {
      "command": "python",
      "args": ["scripts/run_finance_server.py"],
      "cwd": "/absolute/path/to/your/project"
    }
  }
}
```

## 使用示例

### 股票数据查询

```python
# 获取股票实时行情
get_stock_spot(symbol="000001")

# 获取股票历史数据
get_stock_history(symbol="000001", period="daily")

# 获取财务数据
get_stock_financials(symbol="000001")

# 获取技术指标
get_stock_technical_indicators(symbol="000001")
```

### 行业分析

```python
# 获取科技行业新闻
get_industry_news(industry="technology")

# 获取新能源行业政策支持
get_policy_support(industry="new_energy")

# 获取医疗保健行业市场热度
get_market_heat(industry="healthcare")

# 获取金融行业综合概览
get_industry_overview(industry="finance")
```

## 项目结构

详细的项目结构说明请参考 [.cline/project_structure.md](.cline/project_structure.md)

## 技术栈

- **Python 3.8+**: 主要编程语言
- **akshare**: 金融数据获取库
- **MCP (Model Context Protocol)**: 协议标准
- **requests**: HTTP 请求库
- **pandas**: 数据处理库

## 开发

### 运行测试

```bash
pytest
```

### 项目配置

- 使用虚拟环境管理依赖
- 支持 pytest 测试框架
- 遵循 MCP 协议标准
- 包含反爬虫机制
