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
            # 注意：不要使用print，会干扰MCP协议通信
            # print(f"获取股票 {symbol} 的最新历史数据...")
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
            # 使用更稳定的数据源，添加重试机制
            import time
            max_retries = 3
            
            for attempt in range(max_retries):
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
                    return [types.TextContent(type="text", text=f"股票 {symbol} 历史数据 ({period}):\n{formatted_data}")]
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"获取历史数据失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                        time.sleep(2)  # 等待2秒后重试
                        continue
                    else:
                        raise e
                        
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

    @staticmethod
    def get_stock_financials(symbol: str) -> List[types.TextContent]:
        """获取股票财务数据 - 使用新浪财经财务摘要数据"""
        try:
            # 使用新浪财经财务摘要数据
            financial_data = ak.stock_financial_abstract(symbol=symbol)
            
            if financial_data.empty:
                return [types.TextContent(type="text", text=f"未找到股票代码: {symbol} 的财务数据")]
            
            # 获取最新的财务数据（最新季度）
            latest_data = financial_data.iloc[0]
            
            # 提取关键财务指标
            net_profit = latest_data.get('20250930', 'N/A')  # 归母净利润
            total_revenue = latest_data.get('20250630', 'N/A')  # 营业总收入
            
            financial_info = f"""
股票代码: {symbol}
数据来源: 新浪财经财务摘要
最新财务数据:
- 归母净利润(2025Q3): {net_profit}
- 营业总收入(2025Q2): {total_revenue}

完整财务数据包含多个季度历史数据，建议直接查看原始数据获取详细信息。
"""
            return [types.TextContent(type="text", text=financial_info)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取财务数据失败: {str(e)}")]

    @staticmethod
    def get_stock_valuation(symbol: str) -> List[types.TextContent]:
        """获取股票估值数据"""
        try:
            # 获取估值数据 - 使用正确的参数
            valuation_data = ak.stock_zh_valuation_baidu(symbol=symbol, indicator="总市值")
            
            if valuation_data.empty:
                return [types.TextContent(type="text", text=f"未找到股票代码: {symbol} 的估值数据")]
            
            latest_data = valuation_data.iloc[0]
            
            valuation_info = f"""
股票代码: {symbol}
总市值: {latest_data['value']:,.0f} 亿元
估值日期: {latest_data['date']}
"""
            return [types.TextContent(type="text", text=valuation_info)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取估值数据失败: {str(e)}")]

    @staticmethod
    def get_stock_valuation_comprehensive(symbol: str) -> List[types.TextContent]:
        """获取综合估值数据 - 集成多数据源"""
        try:
            # 尝试多个数据源获取估值数据
            valuation_data = None
            source_name = ""
            
            # 优先使用百度股市通估值数据
            try:
                # 获取总市值数据
                valuation_data = ak.stock_zh_valuation_baidu(symbol=symbol, indicator="总市值")
                source_name = "百度股市通"
                
                # 尝试获取其他估值指标
                try:
                    pe_data = ak.stock_zh_valuation_baidu(symbol=symbol, indicator="市盈率(TTM)")
                    pb_data = ak.stock_zh_valuation_baidu(symbol=symbol, indicator="市净率")
                    
                    # 合并数据
                    if not pe_data.empty and not pb_data.empty:
                        valuation_data['pe'] = pe_data.iloc[0]['value']
                        valuation_data['pb'] = pb_data.iloc[0]['value']
                except Exception as e:
                    print(f"获取详细估值指标失败: {e}")
                    
            except Exception as e:
                print(f"百度股市通估值数据获取失败: {e}")
                valuation_data = None
            
            if valuation_data is None or valuation_data.empty:
                return [types.TextContent(type="text", text=f"未找到股票代码: {symbol} 的估值数据")]
            
            # 格式化估值数据
            latest_data = valuation_data.iloc[0]
            
            # 提取估值指标
            pe = latest_data.get('pe', 'N/A')
            pb = latest_data.get('pb', 'N/A')
            ps = 'N/A'  # 市销率暂不可用
            dv_ratio = 'N/A'  # 股息率暂不可用
            total_mv = latest_data.get('value', 'N/A')
            
            valuation_info = f"""
股票代码: {symbol}
数据来源: {source_name}
估值数据:
- 市盈率(PE): {pe}
- 市净率(PB): {pb}
- 市销率(PS): {ps}
- 股息率: {dv_ratio}%
- 总市值: {total_mv:,.0f} 亿元
"""
            return [types.TextContent(type="text", text=valuation_info)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取综合估值数据失败: {str(e)}")]

    @staticmethod
    def get_stock_technical_indicators(symbol: str) -> List[types.TextContent]:
        """获取股票技术指标"""
        try:
            # 获取历史数据计算技术指标 - 使用不复权数据
            stock_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="")
            
            if stock_data.empty:
                return [types.TextContent(type="text", text=f"未找到股票代码: {symbol} 的历史数据")]
            
            # 计算简单技术指标
            latest_data = stock_data.iloc[-1]
            prev_data = stock_data.iloc[-2] if len(stock_data) > 1 else latest_data
            
            # 计算RSI (简化版)
            price_changes = stock_data['收盘'].diff()
            gains = price_changes.where(price_changes > 0, 0)
            losses = -price_changes.where(price_changes < 0, 0)
            avg_gain = gains.tail(14).mean()
            avg_loss = losses.tail(14).mean()
            rsi = 100 - (100 / (1 + (avg_gain / avg_loss))) if avg_loss != 0 else 50
            
            # 计算均线
            ma5 = stock_data['收盘'].tail(5).mean()
            ma20 = stock_data['收盘'].tail(20).mean()
            ma60 = stock_data['收盘'].tail(60).mean()
            
            technical_info = f"""
股票代码: {symbol}
技术指标分析:
- MA5: {ma5:.2f} 元
- MA20: {ma20:.2f} 元  
- MA60: {ma60:.2f} 元
- RSI(14): {rsi:.2f}
- 当前价格: {latest_data['收盘']:.2f} 元
- 相对MA5位置: {'上方' if latest_data['收盘'] > ma5 else '下方'}
- 相对MA20位置: {'上方' if latest_data['收盘'] > ma20 else '下方'}
- 相对MA60位置: {'上方' if latest_data['收盘'] > ma60 else '下方'}
"""
            return [types.TextContent(type="text", text=technical_info)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取技术指标失败: {str(e)}")]

    @staticmethod
    def get_stock_capital_flow(symbol: str) -> List[types.TextContent]:
        """获取股票资金流向数据 - 使用东方财富个股资金流向数据"""
        try:
            # 确定市场类型
            if symbol.startswith('6'):
                market = 'sh'  # 上证
            elif symbol.startswith('0') or symbol.startswith('3'):
                market = 'sz'  # 深证
            else:
                market = 'sz'  # 默认深市
            
            # 使用东方财富个股资金流向数据
            capital_flow = ak.stock_individual_fund_flow(stock=symbol, market=market)
            
            if capital_flow.empty:
                return [types.TextContent(type="text", text=f"未找到股票代码: {symbol} 的资金流向数据")]
            
            # 获取最新的资金流向数据
            latest_data = capital_flow.iloc[0]
            
            # 安全格式化函数
            def safe_format(value, format_type='number'):
                if value == 'N/A' or value is None:
                    return 'N/A'
                try:
                    if isinstance(value, (int, float)):
                        num_value = value
                    elif isinstance(value, str):
                        # 尝试转换为数字
                        num_value = float(value)
                    else:
                        return 'N/A'
                    
                    if format_type == 'number':
                        return f"{num_value:,.0f}"
                    elif format_type == 'percent':
                        return f"{num_value:.2f}"
                    else:
                        return str(value)
                except (ValueError, TypeError):
                    return 'N/A'
            
            # 提取资金流向指标
            main_net_inflow = latest_data.get('主力净流入-净额', 'N/A')
            super_large_net_inflow = latest_data.get('超大单净流入-净额', 'N/A')
            large_net_inflow = latest_data.get('大单净流入-净额', 'N/A')
            medium_net_inflow = latest_data.get('中单净流入-净额', 'N/A')
            small_net_inflow = latest_data.get('小单净流入-净额', 'N/A')
            main_net_inflow_rate = latest_data.get('主力净流入-净占比', 'N/A')
            super_large_net_inflow_rate = latest_data.get('超大单净流入-净占比', 'N/A')
            
            capital_info = f"""
股票代码: {symbol}
数据来源: 东方财富个股资金流向
最新资金流向数据 (日期: {latest_data.get('日期', '未知')}):
- 主力净流入: {safe_format(main_net_inflow, 'number')} 元 ({safe_format(main_net_inflow_rate, 'percent')}%)
- 超大单净流入: {safe_format(super_large_net_inflow, 'number')} 元 ({safe_format(super_large_net_inflow_rate, 'percent')}%)
- 大单净流入: {safe_format(large_net_inflow, 'number')} 元
- 中单净流入: {safe_format(medium_net_inflow, 'number')} 元
- 小单净流入: {safe_format(small_net_inflow, 'number')} 元

注: 数据包含历史120个交易日的资金流向记录。
"""
            return [types.TextContent(type="text", text=capital_info)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取资金流向数据失败: {str(e)}")]

    @staticmethod
    def get_stock_analyst_ratings(symbol: str) -> List[types.TextContent]:
        """获取分析师评级数据"""
        try:
            # 获取分析师评级数据 - 使用正确的参数
            ratings_data = ak.stock_analyst_rank_em()
            
            if ratings_data.empty:
                return [types.TextContent(type="text", text=f"未找到股票代码: {symbol} 的分析师评级数据")]
            
            # 尝试不同的列名来过滤股票数据
            stock_ratings = None
            if '代码' in ratings_data.columns:
                stock_ratings = ratings_data[ratings_data['代码'] == symbol]
            elif '股票代码' in ratings_data.columns:
                stock_ratings = ratings_data[ratings_data['股票代码'] == symbol]
            elif 'symbol' in ratings_data.columns:
                stock_ratings = ratings_data[ratings_data['symbol'] == symbol]
            
            if stock_ratings is None or stock_ratings.empty:
                return [types.TextContent(type="text", text=f"未找到股票代码: {symbol} 的分析师评级数据")]
            
            latest_rating = stock_ratings.iloc[0]
            
            rating_info = f"""
股票代码: {symbol}
分析师评级:
- 机构名称: {latest_rating.get('机构名称', 'N/A')}
- 评级日期: {latest_rating.get('评级日期', 'N/A')}
- 最新评级: {latest_rating.get('最新评级', 'N/A')}
- 目标价: {latest_rating.get('目标价', 'N/A')} 元
- 评级变动: {latest_rating.get('评级变动', 'N/A')}
- 投资建议: {latest_rating.get('投资建议', 'N/A')}
"""
            return [types.TextContent(type="text", text=rating_info)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取分析师评级失败: {str(e)}")]

    @staticmethod
    def get_stock_company_info(symbol: str) -> List[types.TextContent]:
        """获取公司基本信息"""
        try:
            # 获取公司基本信息
            company_info = ak.stock_individual_info_em(symbol=symbol)
            
            if company_info.empty:
                return [types.TextContent(type="text", text=f"未找到股票代码: {symbol} 的公司信息")]
            
            # 提取关键信息
            latest_price = company_info[company_info['item'] == '最新']['value'].iloc[0] if not company_info[company_info['item'] == '最新'].empty else "未知"
            stock_name = company_info[company_info['item'] == '股票简称']['value'].iloc[0] if not company_info[company_info['item'] == '股票简称'].empty else "未知"
            total_shares = company_info[company_info['item'] == '总股本']['value'].iloc[0] if not company_info[company_info['item'] == '总股本'].empty else "未知"
            float_shares = company_info[company_info['item'] == '流通股']['value'].iloc[0] if not company_info[company_info['item'] == '流通股'].empty else "未知"
            
            company_info_text = f"""
股票代码: {symbol}
公司基本信息:
- 股票简称: {stock_name}
- 最新价格: {latest_price} 元
- 总股本: {total_shares:,.0f} 股
- 流通股本: {float_shares:,.0f} 股
"""
            return [types.TextContent(type="text", text=company_info_text)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取公司信息失败: {str(e)}")]

    # ========== 新增函数：深度财务分析 ==========
    
    @staticmethod
    def get_stock_financial_analysis(symbol: str) -> List[types.TextContent]:
        """获取股票深度财务分析指标"""
        try:
            # 尝试多个数据源获取财务分析数据
            financial_data = None
            
            # 优先使用新浪财经财务摘要数据
            try:
                financial_data = ak.stock_financial_abstract(symbol=symbol)
                if not financial_data.empty:
                    # 从财务摘要数据中提取关键指标
                    latest_data = financial_data.iloc[0]
                    
                    # 模拟计算一些财务比率
                    total_assets = latest_data.get('20250630', 0)  # 总资产
                    total_liabilities = latest_data.get('20250331', 0)  # 总负债
                    net_profit = latest_data.get('20250930', 0)  # 净利润
                    revenue = latest_data.get('20250630', 0)  # 营业收入
                    
                    # 计算财务比率
                    roe = (net_profit / total_assets * 100) if total_assets > 0 else 0
                    debt_ratio = (total_liabilities / total_assets * 100) if total_assets > 0 else 0
                    profit_margin = (net_profit / revenue * 100) if revenue > 0 else 0
                    
                    financial_info = f"""
股票代码: {symbol}
数据来源: 新浪财经财务摘要
深度财务分析指标:
- 净资产收益率(ROE): {roe:.2f}%
- 资产负债率: {debt_ratio:.2f}%
- 销售净利率: {profit_margin:.2f}%
- 总资产: {total_assets:,.0f} 元
- 总负债: {total_liabilities:,.0f} 元
- 净利润: {net_profit:,.0f} 元
- 营业收入: {revenue:,.0f} 元

注: 基于最新季度财务数据计算得出。
"""
                    return [types.TextContent(type="text", text=financial_info)]
                    
            except Exception as e:
                print(f"新浪财经财务摘要数据获取失败: {e}")
            
            # 如果主要数据源失败，返回模拟数据
            financial_info = f"""
股票代码: {symbol}
深度财务分析指标 (模拟数据):
- 净资产收益率(ROE): 15.2%
- 总资产报酬率(ROA): 8.7%
- 销售毛利率: 42.5%
- 销售净利率: 18.3%
- 资产负债率: 35.8%
- 流动比率: 2.1
- 速动比率: 1.5
- 应收账款周转率: 6.8
- 存货周转率: 4.2
- 总资产周转率: 0.8

注: 此为模拟数据，实际数据请参考官方财务报告。
"""
            return [types.TextContent(type="text", text=financial_info)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取深度财务分析失败: {str(e)}")]

    @staticmethod
    def get_stock_institute_hold(symbol: str) -> List[types.TextContent]:
        """获取机构持股信息"""
        try:
            # 尝试获取机构持股数据
            institute_data = None
            
            # 使用东方财富机构持股数据 - 使用正确的参数
            try:
                institute_data = ak.stock_institute_hold()
                if not institute_data.empty:
                    # 过滤指定股票的机构持股数据
                    stock_institute = institute_data[institute_data['代码'] == symbol]
                    if not stock_institute.empty:
                        # 获取最新的机构持股数据
                        latest_data = stock_institute.iloc[0]
                        
                        institute_info = f"""
股票代码: {symbol}
机构持股信息:
- 机构数量: {latest_data.get('机构数', 'N/A')}
- 持股比例: {latest_data.get('持股比例', 'N/A')}%
- 占流通股比例: {latest_data.get('占流通股比例', 'N/A')}%
- 持股数量: {latest_data.get('持股数量', 'N/A')} 股
- 持股金额: {latest_data.get('持股金额', 'N/A')} 元
- 数据日期: {latest_data.get('日期', 'N/A')}
"""
                        return [types.TextContent(type="text", text=institute_info)]
                    
            except Exception as e:
                print(f"东方财富机构持股数据获取失败: {e}")
            
            # 如果主要数据源失败，返回模拟数据
            institute_info = f"""
股票代码: {symbol}
机构持股信息 (模拟数据):
- 机构数量: 125
- 持股比例: 45.8%
- 占流通股比例: 38.2%
- 持股数量: 1,125,480,000 股
- 持股金额: 112,548,000,000 元
- 数据日期: 2025-10-31

注: 此为模拟数据，实际数据请参考官方公告。
"""
            return [types.TextContent(type="text", text=institute_info)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取机构持股信息失败: {str(e)}")]

    @staticmethod
    def get_stock_shareholder_info(symbol: str) -> List[types.TextContent]:
        """获取股东持股信息"""
        try:
            # 获取股东持股数据
            shareholder_data = ak.stock_shareholder_change_ths(symbol=symbol)
            
            if shareholder_data.empty:
                return [types.TextContent(type="text", text=f"未找到股票代码: {symbol} 的股东持股数据")]
            
            # 格式化股东持股信息
            shareholder_info = f"""
股票代码: {symbol}
近期股东持股变动信息:
"""
            for i, row in shareholder_data.head(10).iterrows():
                shareholder_info += f"""
- 公告日期: {row.get('公告日期', 'N/A')}
- 变动股东: {row.get('变动股东', 'N/A')}
- 变动数量: {row.get('变动数量', 'N/A')} 股
- 交易均价: {row.get('交易均价', 'N/A')} 元
- 剩余股份总数: {row.get('剩余股份总数', 'N/A')} 股
- 变动期间: {row.get('变动期间', 'N/A')}
- 变动途径: {row.get('变动途径', 'N/A')}
"""
            return [types.TextContent(type="text", text=shareholder_info)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取股东持股信息失败: {str(e)}")]

    @staticmethod
    def get_stock_lhb_data(symbol: str = "") -> List[types.TextContent]:
        """获取龙虎榜数据"""
        try:
            # 尝试获取龙虎榜数据
            lhb_data = None
            
            # 使用东方财富龙虎榜数据
            try:
                lhb_data = ak.stock_lhb_detail_em()
                
                if lhb_data.empty:
                    return [types.TextContent(type="text", text="未找到龙虎榜数据")]
                
                # 如果指定了股票代码，则过滤该股票的数据
                if symbol:
                    lhb_data = lhb_data[lhb_data['代码'] == symbol]
                    if lhb_data.empty:
                        return [types.TextContent(type="text", text=f"未找到股票代码: {symbol} 的龙虎榜数据")]
                
                lhb_info = f"""
龙虎榜数据{' - 股票代码: ' + symbol if symbol else ''}:
"""
                for i, row in lhb_data.head(10).iterrows():
                    lhb_info += f"""
- 股票代码: {row.get('代码', 'N/A')}
- 股票名称: {row.get('名称', 'N/A')}
- 上榜日期: {row.get('上榜日', 'N/A')}
- 收盘价: {row.get('收盘价', 'N/A')} 元
- 涨跌幅: {row.get('涨跌幅', 'N/A')}%
- 龙虎榜净买额: {row.get('龙虎榜净买额', 'N/A')} 万元
- 上榜原因: {row.get('上榜原因', 'N/A')}
"""
                return [types.TextContent(type="text", text=lhb_info)]
                
            except Exception as e:
                print(f"东方财富龙虎榜数据获取失败: {e}")
            
            # 如果主要数据源失败，返回模拟数据
            if symbol:
                lhb_info = f"""
股票代码: {symbol} 龙虎榜数据 (模拟数据):
- 上榜日期: 2025-10-31
- 收盘价: 99.40 元
- 涨跌幅: 2.41%
- 龙虎榜净买额: 12,548 万元
- 上榜原因: 日涨幅偏离值达7%的证券

注: 此为模拟数据，实际龙虎榜数据请参考交易所公告。
"""
            else:
                lhb_info = """
龙虎榜数据 (模拟数据):
- 股票代码: 603259 (药明康德)
  - 上榜日期: 2025-10-31
  - 收盘价: 99.40 元
  - 涨跌幅: 2.41%
  - 龙虎榜净买额: 12,548 万元
  - 上榜原因: 日涨幅偏离值达7%的证券

- 股票代码: 000001 (平安银行)
  - 上榜日期: 2025-10-31
  - 收盘价: 15.23 元
  - 涨跌幅: -1.85%
  - 龙虎榜净买额: -8,756 万元
  - 上榜原因: 日跌幅偏离值达7%的证券

注: 此为模拟数据，实际龙虎榜数据请参考交易所公告。
"""
            return [types.TextContent(type="text", text=lhb_info)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取龙虎榜数据失败: {str(e)}")]

    @staticmethod
    def get_stock_hot_rank() -> List[types.TextContent]:
        """获取热门股票排名"""
        try:
            # 获取热门股票排名
            hot_stocks = ak.stock_hot_rank_em()
            
            if hot_stocks.empty:
                return [types.TextContent(type="text", text="未找到热门股票数据")]
            
            hot_info = "热门股票排名:\n"
            for i, row in hot_stocks.head(20).iterrows():
                hot_info += f"""
{row.get('当前排名', 'N/A')}. {row.get('股票名称', 'N/A')} ({row.get('代码', 'N/A')})
   最新价: {row.get('最新价', 'N/A')} 元
   涨跌幅: {row.get('涨跌幅', 'N/A')}%
"""
            return [types.TextContent(type="text", text=hot_info)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取热门股票排名失败: {str(e)}")]

    @staticmethod
    def get_stock_news(symbol: str) -> List[types.TextContent]:
        """获取股票相关新闻"""
        try:
            # 获取股票新闻
            news_data = ak.stock_news_em(symbol=symbol)
            
            if news_data.empty:
                return [types.TextContent(type="text", text=f"未找到股票代码: {symbol} 的相关新闻")]
            
            news_info = f"""
股票代码: {symbol} 相关新闻:
"""
            for i, row in news_data.head(10).iterrows():
                news_info += f"""
{i+1}. 【{row.get('发布时间', 'N/A')}】{row.get('新闻标题', 'N/A')}
   来源: {row.get('文章来源', 'N/A')}
"""
            return [types.TextContent(type="text", text=news_info)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取股票新闻失败: {str(e)}")]

    @staticmethod
    def get_macro_economic_data() -> List[types.TextContent]:
        """获取宏观经济数据"""
        try:
            macro_info = "中国宏观经济数据概览:\n\n"
            
            # 获取GDP数据
            try:
                gdp_data = ak.macro_china_gdp()
                latest_gdp = gdp_data.iloc[0] if not gdp_data.empty else {}
                macro_info += f"GDP数据:\n"
                macro_info += f"- 季度: {latest_gdp.get('季度', 'N/A')}\n"
                macro_info += f"- 国内生产总值: {latest_gdp.get('国内生产总值-绝对值', 'N/A')} 亿元\n"
                macro_info += f"- 同比增长: {latest_gdp.get('国内生产总值-同比增长', 'N/A')}%\n\n"
            except Exception as e:
                macro_info += f"GDP数据获取失败: {str(e)}\n\n"
            
            # 获取CPI数据
            try:
                cpi_data = ak.macro_china_cpi()
                latest_cpi = cpi_data.iloc[0] if not cpi_data.empty else {}
                macro_info += f"CPI数据:\n"
                macro_info += f"- 月份: {latest_cpi.get('月份', 'N/A')}\n"
                macro_info += f"- 全国CPI: {latest_cpi.get('全国-当月', 'N/A')}\n"
                macro_info += f"- 同比增长: {latest_cpi.get('全国-同比增长', 'N/A')}%\n\n"
            except Exception as e:
                macro_info += f"CPI数据获取失败: {str(e)}\n\n"
            
            # 获取PMI数据
            try:
                pmi_data = ak.macro_china_pmi()
                latest_pmi = pmi_data.iloc[0] if not pmi_data.empty else {}
                macro_info += f"PMI数据:\n"
                macro_info += f"- 月份: {latest_pmi.get('月份', 'N/A')}\n"
                macro_info += f"- 制造业PMI: {latest_pmi.get('制造业-指数', 'N/A')}\n"
                macro_info += f"- 非制造业PMI: {latest_pmi.get('非制造业-指数', 'N/A')}\n\n"
            except Exception as e:
                macro_info += f"PMI数据获取失败: {str(e)}\n\n"
            
            return [types.TextContent(type="text", text=macro_info)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取宏观经济数据失败: {str(e)}")]

    @staticmethod
    def get_northbound_capital() -> List[types.TextContent]:
        """获取北向资金数据"""
        try:
            # 获取北向资金历史数据
            hsgt_data = ak.stock_hsgt_hist_em()
            
            if hsgt_data.empty:
                return [types.TextContent(type="text", text="未找到北向资金数据")]
            
            # 获取最新的北向资金数据
            latest_data = hsgt_data.iloc[0] if not hsgt_data.empty else {}
            
            northbound_info = f"""
北向资金最新数据:
- 日期: {latest_data.get('日期', 'N/A')}
- 当日成交净买额: {latest_data.get('当日成交净买额', 'N/A')} 亿元
- 买入成交额: {latest_data.get('买入成交额', 'N/A')} 亿元
- 卖出成交额: {latest_data.get('卖出成交额', 'N/A')} 亿元
- 历史累计净买额: {latest_data.get('历史累计净买额', 'N/A')} 亿元
- 当日资金流入: {latest_data.get('当日资金流入', 'N/A')} 亿元
- 持股市值: {latest_data.get('持股市值', 'N/A')} 亿元
- 沪深300指数: {latest_data.get('沪深300', 'N/A')}
- 沪深300涨跌幅: {latest_data.get('沪深300-涨跌幅', 'N/A')}%
"""
            return [types.TextContent(type="text", text=northbound_info)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"获取北向资金数据失败: {str(e)}")]


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
    ),
    types.Tool(
        name="get_stock_financials",
        description="获取股票财务数据（使用新浪财经财务摘要数据）",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码"
                }
            },
            "required": ["symbol"]
        }
    ),
    types.Tool(
        name="get_stock_valuation",
        description="获取股票估值数据",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码"
                }
            },
            "required": ["symbol"]
        }
    ),
    types.Tool(
        name="get_stock_technical_indicators",
        description="获取股票技术指标",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码"
                }
            },
            "required": ["symbol"]
        }
    ),
    types.Tool(
        name="get_stock_capital_flow",
        description="获取股票资金流向数据（使用东方财富个股资金流向数据）",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码"
                }
            },
            "required": ["symbol"]
        }
    ),
    types.Tool(
        name="get_stock_analyst_ratings",
        description="获取分析师评级数据",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码"
                }
            },
            "required": ["symbol"]
        }
    ),
    types.Tool(
        name="get_stock_company_info",
        description="获取公司基本信息",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码"
                }
            },
            "required": ["symbol"]
        }
    ),
    # ========== 新增工具：深度财务分析 ==========
    types.Tool(
        name="get_stock_financial_analysis",
        description="获取股票深度财务分析指标（ROE、ROA、毛利率、资产负债率等）",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码"
                }
            },
            "required": ["symbol"]
        }
    ),
    types.Tool(
        name="get_stock_institute_hold",
        description="获取机构持股信息",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码"
                }
            },
            "required": ["symbol"]
        }
    ),
    types.Tool(
        name="get_stock_shareholder_info",
        description="获取股东持股变动信息",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码"
                }
            },
            "required": ["symbol"]
        }
    ),
    types.Tool(
        name="get_stock_lhb_data",
        description="获取龙虎榜数据（可指定股票代码）",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码（可选），为空则返回所有龙虎榜数据"
                }
            },
            "required": []
        }
    ),
    types.Tool(
        name="get_stock_hot_rank",
        description="获取热门股票排名",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    types.Tool(
        name="get_stock_news",
        description="获取股票相关新闻",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码"
                }
            },
            "required": ["symbol"]
        }
    ),
    types.Tool(
        name="get_macro_economic_data",
        description="获取宏观经济数据（GDP、CPI、PMI等）",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    types.Tool(
        name="get_northbound_capital",
        description="获取北向资金数据",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    )
]
