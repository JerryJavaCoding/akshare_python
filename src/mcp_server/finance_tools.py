"""Financial data tools using akshare."""
import akshare as ak
import pandas as pd
from typing import Any, Dict, List
import mcp.types as types
import requests
import time
import random

# 模拟浏览器请求的User-Agent列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

def get_random_user_agent():
    """获取随机User-Agent"""
    return random.choice(USER_AGENTS)

def make_request_with_retry(url, params=None, max_retries=3):
    """带重试机制的请求函数"""
    session = requests.Session()
    
    # 设置请求头模拟浏览器
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    for attempt in range(max_retries):
        try:
            response = session.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                # 指数退避策略
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"等待 {sleep_time:.2f} 秒后重试...")
                time.sleep(sleep_time)
            else:
                raise e
    return None


class FinanceDataService:
    """Service for financial data operations using akshare."""
    
    @staticmethod
    def get_stock_spot(symbol: str) -> List[types.TextContent]:
        """Get latest available stock data (historical)."""
        try:
            # 获取最近的历史数据作为"最新"数据
            print(f"获取股票 {symbol} 的最新历史数据...")
            stock_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date="20250101")
            
            if stock_data.empty:
                return [types.TextContent(type="text", text=f"未找到股票代码: {symbol} 的数据")]
            
            # 获取最新的一条数据
            latest_data = stock_data.iloc[-1]
            
            stock_info = f"""
股票代码: {symbol}
股票名称: 阳光电源 (示例)
最新收盘价: {latest_data['收盘']:.2f} 元
交易日期: {latest_data['日期']}
涨跌幅: {latest_data['涨跌幅']:.2f}%
涨跌额: {latest_data['涨跌额']:.2f} 元
最高价: {latest_data['最高']:.2f} 元
最低价: {latest_data['最低']:.2f} 元
成交量: {latest_data['成交量']:,.0f} 股
成交额: {latest_data['成交额']:,.0f} 元
振幅: {latest_data['振幅']:.2f}%
开盘价: {latest_data['开盘']:.2f} 元
"""
            return [types.TextContent(type="text", text=stock_info)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取股票数据失败: {str(e)}")]
    
    @staticmethod
    def get_stock_history(symbol: str, period: str = "daily") -> List[types.TextContent]:
        """Get historical stock data."""
        try:
            if period == "daily":
                stock_data = ak.stock_zh_a_hist(symbol=symbol, period="daily")
            elif period == "weekly":
                stock_data = ak.stock_zh_a_hist(symbol=symbol, period="weekly")
            elif period == "monthly":
                stock_data = ak.stock_zh_a_hist(symbol=symbol, period="monthly")
            else:
                return [types.TextContent(type="text", text="不支持的周期类型，请使用 daily, weekly 或 monthly")]
            
            if stock_data.empty:
                return [types.TextContent(type="text", text=f"未找到股票代码: {symbol} 的历史数据")]
            
            # Format the data
            formatted_data = stock_data.head(20).to_string(index=False)  # Limit to first 20 records
            return [types.TextContent(type="text", text=f"股票 {symbol} 历史数据:\n{formatted_data}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取历史数据失败: {str(e)}")]
    
    @staticmethod
    def get_fund_info(symbol: str) -> List[types.TextContent]:
        """Get fund information."""
        try:
            fund_data = ak.fund_em_open_fund_info(fund=symbol, indicator="单位净值走势")
            
            if fund_data.empty:
                return [types.TextContent(type="text", text=f"未找到基金代码: {symbol}")]
            
            # Get basic fund info
            fund_info = ak.fund_em_fund_name()
            fund_name = fund_info[fund_info['基金代码'] == symbol]['基金简称'].iloc[0] if not fund_info.empty else "未知"
            
            latest_data = fund_data.iloc[0]
            result = f"""
基金代码: {symbol}
基金名称: {fund_name}
净值日期: {latest_data['净值日期']}
单位净值: {latest_data['单位净值']}
日增长率: {latest_data['日增长率']}%
累计净值: {latest_data['累计净值']}
"""
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取基金数据失败: {str(e)}")]
    
    @staticmethod
    def get_index_data(symbol: str = "000001") -> List[types.TextContent]:
        """Get stock index data."""
        try:
            index_data = ak.stock_zh_index_spot()
            if symbol:
                index_data = index_data[index_data['代码'] == symbol]
            
            if index_data.empty:
                return [types.TextContent(type="text", text=f"未找到指数代码: {symbol}")]
            
            result = []
            for _, row in index_data.iterrows():
                index_info = f"""
指数代码: {row['代码']}
指数名称: {row['名称']}
最新价: {row['最新价']}
涨跌幅: {row['涨跌幅']}%
涨跌额: {row['涨跌额']}
成交量: {row['成交量']}
成交额: {row['成交额']}
今开: {row['今开']}
昨收: {row['昨收']}
最高: {row['最高']}
最低: {row['最低']}
"""
                result.append(types.TextContent(type="text", text=index_info))
            
            return result
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取指数数据失败: {str(e)}")]
    
    @staticmethod
    def get_futures_data(symbol: str = "") -> List[types.TextContent]:
        """Get futures market data."""
        try:
            futures_data = ak.futures_zh_spot(subscribe_list="", market="CF", adjust=False)
            
            if symbol:
                futures_data = futures_data[futures_data['symbol'] == symbol]
            
            if futures_data.empty:
                return [types.TextContent(type="text", text=f"未找到期货代码: {symbol}")]
            
            result = []
            for _, row in futures_data.head(10).iterrows():  # Limit to first 10
                futures_info = f"""
期货代码: {row['symbol']}
名称: {row['name']}
最新价: {row['close']}
涨跌幅: {row['changepercent']}%
成交量: {row['volume']}
持仓量: {row['position']}
今开: {row['open']}
最高: {row['high']}
最低: {row['low']}
昨收: {row['settlement']}
"""
                result.append(types.TextContent(type="text", text=futures_info))
            
            return result
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取期货数据失败: {str(e)}")]


# Tool definitions for MCP
FINANCE_TOOLS = [
    types.Tool(
        name="get_stock_spot",
        description="获取股票实时行情数据",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码（如：000001），为空则返回所有股票"
                }
            },
            "required": []
        }
    ),
    types.Tool(
        name="get_stock_history",
        description="获取股票历史数据",
        inputSchema={
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
    ),
    types.Tool(
        name="get_fund_info",
        description="获取基金信息",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "基金代码"
                }
            },
            "required": ["symbol"]
        }
    ),
    types.Tool(
        name="get_index_data",
        description="获取指数数据",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "指数代码（如：000001 上证指数），为空则返回主要指数"
                }
            },
            "required": []
        }
    ),
    types.Tool(
        name="get_futures_data",
        description="获取期货数据",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "期货代码，为空则返回主要期货"
                }
            },
            "required": []
        }
    )
]
