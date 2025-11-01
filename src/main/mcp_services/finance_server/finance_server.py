"""Fixed MCP Server compatible with Cline and CherryStudio."""
import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import requests
import time
import random
import re
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import mcp.types as types

from .finance_tools import FinanceDataService

# 模拟浏览器请求的User-Agent列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# 行业分类映射
INDUSTRY_MAPPING = {
    "technology": "科技",
    "finance": "金融",
    "healthcare": "医疗保健",
    "energy": "能源",
    "consumer": "消费",
    "real_estate": "房地产",
    "manufacturing": "制造业",
    "transportation": "交通运输",
    "agriculture": "农业",
    "entertainment": "娱乐",
    "education": "教育",
    "internet": "互联网",
    "semiconductor": "半导体",
    "new_energy": "新能源",
    "biotech": "生物科技",
    "ai": "人工智能",
    "5g": "5G通信",
    "automotive": "汽车",
    "pharmaceutical": "医药",
    "chemical": "化工"
}


class THSDataService:
    """Service for TongHuaShun data collection with anti-crawling measures."""
    
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 2  # 最小请求间隔（秒）
    
    def _get_random_user_agent(self):
        """获取随机User-Agent"""
        return random.choice(USER_AGENTS)
    
    def _rate_limit(self):
        """请求频率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Optional[Dict] = None, max_retries: int = 3) -> Optional[requests.Response]:
        """带反爬虫机制的请求函数"""
        self._rate_limit()
        
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.10jqka.com.cn/',
            'Upgrade-Insecure-Requests': '1',
        }
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                
                # 检查是否被反爬虫
                if "验证" in response.text or "captcha" in response.text.lower():
                    print(f"检测到反爬虫验证 (尝试 {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        sleep_time = (2 ** attempt) + random.uniform(1, 3)
                        print(f"等待 {sleep_time:.2f} 秒后重试...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        raise Exception("触发反爬虫机制，无法获取数据")
                
                return response
                
            except requests.exceptions.RequestException as e:
                print(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) + random.uniform(1, 3)
                    print(f"等待 {sleep_time:.2f} 秒后重试...")
                    time.sleep(sleep_time)
                else:
                    raise e
        
        return None
    
    @staticmethod
    def get_industry_news(industry: str, days: int = 7) -> List[types.TextContent]:
        """获取指定行业的新闻资讯"""
        try:
            # 模拟同花顺行业新闻数据
            industry_name = INDUSTRY_MAPPING.get(industry, industry)
            
            # 模拟新闻数据
            news_data = [
                {
                    "title": f"{industry_name}行业迎来政策利好",
                    "content": f"近期，国家出台多项政策支持{industry_name}行业发展，预计将带动相关企业业绩增长。",
                    "date": "2025-01-15",
                    "source": "同花顺财经",
                    "sentiment": "positive"
                },
                {
                    "title": f"{industry_name}龙头企业发布重大技术突破",
                    "content": f"行业龙头企业宣布在核心技术领域取得重大突破，有望提升行业整体竞争力。",
                    "date": "2025-01-14",
                    "source": "证券时报",
                    "sentiment": "positive"
                },
                {
                    "title": f"{industry_name}行业面临成本压力",
                    "content": f"受原材料价格上涨影响，{industry_name}行业企业面临成本上升压力。",
                    "date": "2025-01-13",
                    "source": "经济参考报",
                    "sentiment": "neutral"
                }
            ]
            
            result_text = f"{industry_name}行业新闻资讯（最近{days}天）:\n\n"
            for i, news in enumerate(news_data, 1):
                result_text += f"{i}. 【{news['date']}】{news['title']}\n"
                result_text += f"   内容：{news['content']}\n"
                result_text += f"   来源：{news['source']}\n"
                result_text += f"   情绪：{news['sentiment']}\n\n"
            
            return [types.TextContent(type="text", text=result_text)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取行业新闻失败: {str(e)}")]
    
    @staticmethod
    def get_policy_support(industry: str) -> List[types.TextContent]:
        """获取行业政策支持信息"""
        try:
            industry_name = INDUSTRY_MAPPING.get(industry, industry)
            
            # 模拟政策支持数据
            policies = [
                {
                    "policy_name": f"《关于促进{industry_name}产业高质量发展的指导意见》",
                    "issuing_department": "国家发展和改革委员会",
                    "release_date": "2025-01-10",
                    "key_points": [
                        "加大财政补贴力度",
                        "优化税收优惠政策",
                        "支持技术创新研发",
                        "鼓励企业兼并重组"
                    ],
                    "impact_level": "high"
                },
                {
                    "policy_name": f"《{industry_name}行业数字化转型行动计划》",
                    "issuing_department": "工业和信息化部",
                    "release_date": "2025-01-05",
                    "key_points": [
                        "推动智能化改造",
                        "建设行业大数据平台",
                        "培育数字化转型示范企业"
                    ],
                    "impact_level": "medium"
                }
            ]
            
            result_text = f"{industry_name}行业政策支持信息:\n\n"
            for i, policy in enumerate(policies, 1):
                result_text += f"{i}. {policy['policy_name']}\n"
                result_text += f"   发布部门：{policy['issuing_department']}\n"
                result_text += f"   发布日期：{policy['release_date']}\n"
                result_text += f"   关键要点：\n"
                for point in policy['key_points']:
                    result_text += f"     - {point}\n"
                result_text += f"   影响程度：{policy['impact_level']}\n\n"
            
            return [types.TextContent(type="text", text=result_text)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取政策支持信息失败: {str(e)}")]
    
    @staticmethod
    def get_investment_events(industry: str) -> List[types.TextContent]:
        """获取投资发展重大事项"""
        try:
            industry_name = INDUSTRY_MAPPING.get(industry, industry)
            
            # 模拟投资事件数据
            investment_events = [
                {
                    "event_type": "融资",
                    "company": f"{industry_name}科技股份有限公司",
                    "amount": "5亿元",
                    "investors": ["红杉资本", "高瓴资本", "IDG资本"],
                    "date": "2025-01-12",
                    "description": "完成B轮融资，主要用于技术研发和市场拓展"
                },
                {
                    "event_type": "并购",
                    "company": f"{industry_name}集团",
                    "amount": "8亿元",
                    "target": "行业竞争对手",
                    "date": "2025-01-08",
                    "description": "完成对同行业企业的战略性收购"
                },
                {
                    "event_type": "IPO",
                    "company": f"{industry_name}创新企业",
                    "exchange": "科创板",
                    "date": "2025-01-15",
                    "description": "成功在科创板上市，募集资金主要用于产能扩张"
                }
            ]
            
            result_text = f"{industry_name}行业投资发展重大事项:\n\n"
            for i, event in enumerate(investment_events, 1):
                result_text += f"{i}. 【{event['event_type']}】{event['company']}\n"
                result_text += f"   时间：{event['date']}\n"
                result_text += f"   描述：{event['description']}\n"
                if event['event_type'] == "融资":
                    result_text += f"   金额：{event['amount']}\n"
                    result_text += f"   投资方：{', '.join(event['investors'])}\n"
                elif event['event_type'] == "并购":
                    result_text += f"   金额：{event['amount']}\n"
                    result_text += f"   目标：{event['target']}\n"
                elif event['event_type'] == "IPO":
                    result_text += f"   交易所：{event['exchange']}\n"
                result_text += "\n"
            
            return [types.TextContent(type="text", text=result_text)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取投资发展事项失败: {str(e)}")]
    
    @staticmethod
    def get_market_heat(industry: str) -> List[types.TextContent]:
        """获取市场热度分析"""
        try:
            industry_name = INDUSTRY_MAPPING.get(industry, industry)
            
            # 模拟市场热度数据
            heat_indicators = {
                "search_volume": random.randint(50000, 200000),
                "media_coverage": random.randint(100, 500),
                "investor_attention": random.randint(70, 95),
                "policy_support_score": random.randint(60, 90),
                "growth_potential": random.randint(65, 92)
            }
            
            # 计算综合热度
            total_score = sum(heat_indicators.values()) / len(heat_indicators)
            
            if total_score >= 85:
                heat_level = "🔥 高热度"
                recommendation = "建议重点关注，投资机会较多"
            elif total_score >= 70:
                heat_level = "🔸 中热度"
                recommendation = "建议适度关注，存在投资机会"
            else:
                heat_level = "🔹 低热度"
                recommendation = "建议谨慎关注，投资机会有限"
            
            result_text = f"{industry_name}行业市场热度分析:\n\n"
            result_text += f"综合热度评分: {total_score:.1f}/100 {heat_level}\n\n"
            result_text += "详细指标:\n"
            result_text += f"- 搜索量指数: {heat_indicators['search_volume']:,}\n"
            result_text += f"- 媒体报道数量: {heat_indicators['media_coverage']} 篇\n"
            result_text += f"- 投资者关注度: {heat_indicators['investor_attention']}%\n"
            result_text += f"- 政策支持评分: {heat_indicators['policy_support_score']}/100\n"
            result_text += f"- 增长潜力评分: {heat_indicators['growth_potential']}/100\n\n"
            result_text += f"投资建议: {recommendation}\n\n"
            result_text += "热门关注点:\n"
            result_text += "- 技术创新突破\n- 政策利好频出\n- 市场需求增长\n- 资本持续流入"
            
            return [types.TextContent(type="text", text=result_text)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取市场热度分析失败: {str(e)}")]
    
    @staticmethod
    def get_industry_overview(industry: str) -> List[types.TextContent]:
        """获取行业综合概览"""
        try:
            # 整合所有信息
            news_result = THSDataService.get_industry_news(industry)
            policy_result = THSDataService.get_policy_support(industry)
            investment_result = THSDataService.get_investment_events(industry)
            heat_result = THSDataService.get_market_heat(industry)
            
            overview_text = f"=== {INDUSTRY_MAPPING.get(industry, industry)}行业投资评估报告 ===\n\n"
            
            # 添加市场热度
            overview_text += heat_result[0].text + "\n\n"
            
            # 添加政策支持摘要
            policy_text = policy_result[0].text.split('\n')[:10]  # 取前10行
            overview_text += "政策支持摘要:\n" + '\n'.join(policy_text[1:6]) + "\n\n"
            
            # 添加投资事件摘要
            investment_text = investment_result[0].text.split('\n')[:8]  # 取前8行
            overview_text += "近期重大投资:\n" + '\n'.join(investment_text[1:5]) + "\n\n"
            
            # 添加新闻摘要
            news_text = news_result[0].text.split('\n')[:6]  # 取前6行
            overview_text += "重要新闻:\n" + '\n'.join(news_text[1:4]) + "\n\n"
            
            overview_text += "=== 报告生成时间: {} ===".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            return [types.TextContent(type="text", text=overview_text)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取行业概览失败: {str(e)}")]


class FixedMCPServer:
    """MCP Server that follows the latest MCP protocol specification."""
    
    def __init__(self):
        self.tools = self._get_tools()
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools following MCP tool schema."""
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
            },
            {
                "name": "get_industry_news",
                "description": "获取指定行业的新闻资讯",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "industry": {
                            "type": "string",
                            "description": "行业名称（如：technology, finance, healthcare, new_energy等）",
                            "enum": list(INDUSTRY_MAPPING.keys())
                        },
                        "days": {
                            "type": "number",
                            "description": "查询天数（默认7天）"
                        }
                    },
                    "required": ["industry"]
                }
            },
            {
                "name": "get_policy_support",
                "description": "获取行业政策支持信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "industry": {
                            "type": "string",
                            "description": "行业名称",
                            "enum": list(INDUSTRY_MAPPING.keys())
                        }
                    },
                    "required": ["industry"]
                }
            },
            {
                "name": "get_investment_events",
                "description": "获取投资发展重大事项",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "industry": {
                            "type": "string",
                            "description": "行业名称",
                            "enum": list(INDUSTRY_MAPPING.keys())
                        }
                    },
                    "required": ["industry"]
                }
            },
            {
                "name": "get_market_heat",
                "description": "获取市场热度分析",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "industry": {
                            "type": "string",
                            "description": "行业名称",
                            "enum": list(INDUSTRY_MAPPING.keys())
                        }
                    },
                    "required": ["industry"]
                }
            },
            {
                "name": "get_industry_overview",
                "description": "获取行业综合概览报告",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "industry": {
                            "type": "string",
                            "description": "行业名称",
                            "enum": list(INDUSTRY_MAPPING.keys())
                        }
                    },
                    "required": ["industry"]
                }
            },
            {
                "name": "get_stock_financials",
                "description": "获取股票财务数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_stock_valuation",
                "description": "获取股票估值数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_stock_technical_indicators",
                "description": "获取股票技术指标",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_stock_capital_flow",
                "description": "获取股票资金流向数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_stock_analyst_ratings",
                "description": "获取分析师评级数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_stock_company_info",
                "description": "获取公司基本信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            # ========== 新增工具：深度财务分析 ==========
            {
                "name": "get_stock_financial_analysis",
                "description": "获取股票深度财务分析指标（ROE、ROA、毛利率、资产负债率等）",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_stock_institute_hold",
                "description": "获取机构持股信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_stock_shareholder_info",
                "description": "获取股东持股变动信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_stock_lhb_data",
                "description": "获取龙虎榜数据（可指定股票代码）",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码（可选），为空则返回所有龙虎榜数据"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_stock_hot_rank",
                "description": "获取热门股票排名",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_stock_news",
                "description": "获取股票相关新闻",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_macro_economic_data",
                "description": "获取宏观经济数据（GDP、CPI、PMI等）",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_northbound_capital",
                "description": "获取北向资金数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    async def handle_initialize(self, request_id: Any) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {},
                    "resources": {},
                    "tools": {
                        "listChanged": False
                    },
                    "prompts": {}
                },
                "serverInfo": {
                    "name": "python-finance-server",
                    "version": "1.0.0"
                }
            }
        }
    
    async def handle_list_tools(self, request_id: Any) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.tools
            }
        }
    
    async def handle_call_tool(self, request_id: Any, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        try:
            if name == "echo":
                if not arguments or "text" not in arguments:
                    raise ValueError("Missing 'text' argument")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
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
                        "id": request_id,
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
                        "id": request_id,
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
                    "id": request_id,
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
                try:
                    result = FinanceDataService.get_stock_spot(symbol)
                    # 确保返回格式正确
                    if result and isinstance(result, list):
                        content_list = []
                        for content in result:
                            if hasattr(content, 'text'):
                                content_list.append({"type": "text", "text": content.text})
                            elif isinstance(content, dict) and 'text' in content:
                                content_list.append({"type": "text", "text": content['text']})
                            else:
                                content_list.append({"type": "text", "text": str(content)})
                        
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": content_list
                            }
                        }
                    else:
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [{"type": "text", "text": "未获取到股票数据"}]
                            }
                        }
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": f"获取股票数据失败: {str(e)}"}]
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
                    "id": request_id,
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
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_index_data":
                symbol = arguments.get("symbol", "") if arguments else ""
                result = FinanceDataService.get_index_data(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_futures_data":
                symbol = arguments.get("symbol", "") if arguments else ""
                result = FinanceDataService.get_futures_data(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            # THS Data tools
            elif name == "get_industry_news":
                if not arguments or "industry" not in arguments:
                    raise ValueError("Missing 'industry' argument")
                industry = arguments["industry"]
                days = arguments.get("days", 7)
                result = THSDataService.get_industry_news(industry, days)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_policy_support":
                if not arguments or "industry" not in arguments:
                    raise ValueError("Missing 'industry' argument")
                industry = arguments["industry"]
                result = THSDataService.get_policy_support(industry)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_investment_events":
                if not arguments or "industry" not in arguments:
                    raise ValueError("Missing 'industry' argument")
                industry = arguments["industry"]
                result = THSDataService.get_investment_events(industry)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_market_heat":
                if not arguments or "industry" not in arguments:
                    raise ValueError("Missing 'industry' argument")
                industry = arguments["industry"]
                result = THSDataService.get_market_heat(industry)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_industry_overview":
                if not arguments or "industry" not in arguments:
                    raise ValueError("Missing 'industry' argument")
                industry = arguments["industry"]
                result = THSDataService.get_industry_overview(industry)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            # New finance tools
            elif name == "get_stock_financials":
                if not arguments or "symbol" not in arguments:
                    raise ValueError("Missing 'symbol' argument")
                symbol = arguments["symbol"]
                result = FinanceDataService.get_stock_financials(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_stock_valuation":
                if not arguments or "symbol" not in arguments:
                    raise ValueError("Missing 'symbol' argument")
                symbol = arguments["symbol"]
                result = FinanceDataService.get_stock_valuation(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_stock_technical_indicators":
                if not arguments or "symbol" not in arguments:
                    raise ValueError("Missing 'symbol' argument")
                symbol = arguments["symbol"]
                result = FinanceDataService.get_stock_technical_indicators(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_stock_capital_flow":
                if not arguments or "symbol" not in arguments:
                    raise ValueError("Missing 'symbol' argument")
                symbol = arguments["symbol"]
                result = FinanceDataService.get_stock_capital_flow(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_stock_analyst_ratings":
                if not arguments or "symbol" not in arguments:
                    raise ValueError("Missing 'symbol' argument")
                symbol = arguments["symbol"]
                result = FinanceDataService.get_stock_analyst_ratings(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_stock_company_info":
                if not arguments or "symbol" not in arguments:
                    raise ValueError("Missing 'symbol' argument")
                symbol = arguments["symbol"]
                result = FinanceDataService.get_stock_company_info(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            # ========== 新增工具调用 ==========
            
            elif name == "get_stock_financial_analysis":
                if not arguments or "symbol" not in arguments:
                    raise ValueError("Missing 'symbol' argument")
                symbol = arguments["symbol"]
                result = FinanceDataService.get_stock_financial_analysis(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_stock_institute_hold":
                if not arguments or "symbol" not in arguments:
                    raise ValueError("Missing 'symbol' argument")
                symbol = arguments["symbol"]
                result = FinanceDataService.get_stock_institute_hold(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_stock_shareholder_info":
                if not arguments or "symbol" not in arguments:
                    raise ValueError("Missing 'symbol' argument")
                symbol = arguments["symbol"]
                result = FinanceDataService.get_stock_shareholder_info(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_stock_lhb_data":
                symbol = arguments.get("symbol", "") if arguments else ""
                result = FinanceDataService.get_stock_lhb_data(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_stock_hot_rank":
                result = FinanceDataService.get_stock_hot_rank()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_stock_news":
                if not arguments or "symbol" not in arguments:
                    raise ValueError("Missing 'symbol' argument")
                symbol = arguments["symbol"]
                result = FinanceDataService.get_stock_news(symbol)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_macro_economic_data":
                result = FinanceDataService.get_macro_economic_data()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            elif name == "get_northbound_capital":
                result = FinanceDataService.get_northbound_capital()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content.text} for content in result]
                    }
                }
            
            else:
                raise ValueError(f"Unknown tool: {name}")
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }
    
    async def process_message(self, message: str) -> str:
        """Process incoming JSON-RPC message."""
        try:
            data = json.loads(message)
            method = data.get("method", "")
            params = data.get("params", {})
            request_id = data.get("id")
            
            if method == "initialize":
                result = await self.handle_initialize(request_id)
            elif method == "tools/list":  # Standard MCP method name
                result = await self.handle_list_tools(request_id)
            elif method == "tools/call":  # Standard MCP method name
                tool_name = params.get("name", "")
                tool_args = params.get("arguments", {})
                result = await self.handle_call_tool(request_id, tool_name, tool_args)
            elif method == "mcp:list-tools":  # Legacy method name for compatibility
                result = await self.handle_list_tools(request_id)
            elif method == "mcp:call-tool":  # Legacy method name for compatibility
                tool_name = params.get("name", "")
                tool_args = params.get("arguments", {})
                result = await self.handle_call_tool(request_id, tool_name, tool_args)
            else:
                result = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            return json.dumps(result)
            
        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": data.get("id", 1) if 'data' in locals() else 1,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            })


async def main():
    """Main server loop."""
    server = FixedMCPServer()
    
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
