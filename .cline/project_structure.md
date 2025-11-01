# akshare_python 项目结构说明

## 项目概述
这是一个基于 Python 的 MCP (Model Context Protocol) 服务器项目，主要提供金融数据服务，使用 akshare 库获取股票、基金、期货等金融数据。

## 项目结构

```
akshare_python/
├── .cline/                          # Cline 配置文件夹
│   ├── python_exec.md               # Python 执行规则配置
│   └── project_structure.md         # 项目结构说明 (本文件)
├── docs/                            # 文档文件夹
│   ├── CLINE_USAGE_GUIDE.md         # Cline 使用指南
│   ├── CLINE_VENV_USAGE.md          # 虚拟环境使用指南
│   ├── CONFIGURATION.md             # 配置说明
│   └── MCP_CONNECTION_GUIDE.md      # MCP 连接指南
├── output/                          # 输出文件夹
├── prompt/                          # 提示词文件夹
│   └── 股票分析维度.md              # 股票分析维度说明
├── scripts/                         # 脚本文件夹
│   └── run_finance_server.py        # 金融服务器启动脚本
├── src/                             # 源代码文件夹
│   ├── mcp_server/                  # MCP 服务器模块
│   │   ├── __init__.py              # 模块初始化文件
│   │   ├── finance_server.py        # 金融数据服务器主文件
│   │   └── finance_tools.py         # 金融数据工具函数
│   ├── tests/                       # 测试文件夹
│   │   ├── test_integrated_server.py # 集成测试
│   │   └── test_server.py           # 服务器测试
│   └── mcp_python_project.egg-info/ # Python 包信息
├── .gitignore                       # Git 忽略文件
├── pyproject.toml                   # Python 项目配置
└── README.md                        # 项目说明文档
```

## 核心文件说明

### 主要代码文件
- **src/mcp_server/finance_server.py**: MCP 服务器主文件，处理工具调用和请求分发
- **src/mcp_server/finance_tools.py**: 金融数据工具实现，包含所有数据获取功能

### 配置和文档
- **.cline/python_exec.md**: Cline Python 执行规则配置
- **pyproject.toml**: Python 项目依赖和配置
- **docs/**: 详细的使用和配置文档

### 运行脚本
- **scripts/run_finance_server.py**: 服务器启动脚本

## 服务功能

### 基础工具
- `echo`: 回显输入文本
- `calculate`: 基础数学计算
- `get_time`: 获取当前时间

### 金融数据工具
- **股票数据**: 实时行情、历史数据、财务数据、估值数据、技术指标
- **基金数据**: 基金信息、净值走势
- **指数数据**: 主要指数行情
- **期货数据**: 期货市场数据
- **资金流向**: 股票资金流向分析
- **分析师评级**: 专业分析师评级数据
- **公司信息**: 上市公司基本信息

### 行业分析工具
- **行业新闻**: 各行业最新资讯
- **政策支持**: 行业政策信息
- **投资事件**: 重大投资发展事项
- **市场热度**: 行业市场热度分析
- **行业概览**: 综合行业评估报告

## 技术栈
- **Python 3.8+**: 主要编程语言
- **akshare**: 金融数据获取库
- **MCP (Model Context Protocol)**: 协议标准
- **requests**: HTTP 请求库
- **pandas**: 数据处理库

## 开发说明
- 使用虚拟环境管理依赖
- 支持 pytest 测试框架
- 遵循 MCP 协议标准
- 包含反爬虫机制
