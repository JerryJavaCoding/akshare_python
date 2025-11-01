#!/usr/bin/env python3
"""
全面测试MCP金融工具的有效性
使用山东矿机（002526）作为测试股票
"""

import json
import time
import sys
import subprocess
import os
from typing import Dict, List, Any

class MCPTester:
    def __init__(self, test_symbol="002526"):
        self.test_symbol = test_symbol
        self.server_process = None
        self.results = {}
        
    def start_mcp_server(self):
        """启动MCP服务器"""
        print("🚀 启动MCP服务器...")
        try:
            # 启动MCP服务器进程
            self.server_process = subprocess.Popen(
                [sys.executable, "mcp_services/finance_server/finance_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            time.sleep(2)  # 等待服务器启动
            print("✅ MCP服务器已启动")
            return True
        except Exception as e:
            print(f"❌ 启动MCP服务器失败: {e}")
            return False
    
    def send_mcp_request(self, method: str, params: Dict = None, request_id: int = 1) -> Dict:
        """发送MCP请求"""
        if not self.server_process:
            return {"error": "服务器未启动"}
        
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }
        
        try:
            # 发送请求
            self.server_process.stdin.write(json.dumps(request) + "\n")
            self.server_process.stdin.flush()
            
            # 读取响应
            response_line = self.server_process.stdout.readline().strip()
            if response_line:
                return json.loads(response_line)
            else:
                return {"error": "无响应"}
                
        except Exception as e:
            return {"error": f"请求失败: {e}"}
    
    def test_tool_list(self):
        """测试获取工具列表"""
        print("\n🔧 测试: 获取工具列表")
        response = self.send_mcp_request("tools/list")
        
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"✅ 成功获取到 {len(tools)} 个工具")
            return tools
        else:
            print(f"❌ 获取工具列表失败: {response.get('error', '未知错误')}")
            return []
    
    def test_tool(self, tool_name: str, params: Dict) -> Dict:
        """测试单个工具"""
        print(f"\n🔍 测试: {tool_name}")
        print(f"   参数: {params}")
        
        start_time = time.time()
        response = self.send_mcp_request("tools/call", {
            "name": tool_name,
            "arguments": params
        })
        elapsed_time = time.time() - start_time
        
        result = {
            "tool": tool_name,
            "params": params,
            "response": response,
            "elapsed_time": elapsed_time,
            "success": False,
            "error": None,
            "data_preview": None
        }
        
        if "result" in response:
            result["success"] = True
            if "content" in response["result"] and response["result"]["content"]:
                content_text = response["result"]["content"][0].get("text", "")
                result["data_preview"] = content_text[:200] + "..." if len(content_text) > 200 else content_text
                print(f"✅ 成功 - 耗时: {elapsed_time:.2f}秒")
                print(f"   数据预览: {result['data_preview']}")
            else:
                print(f"⚠️ 成功但无数据 - 耗时: {elapsed_time:.2f}秒")
        else:
            result["success"] = False
            if isinstance(response, dict):
                result["error"] = response.get("error", {}).get("message", "未知错误")
            else:
                result["error"] = str(response)
            print(f"❌ 失败 - 耗时: {elapsed_time:.2f}秒")
            print(f"   错误: {result['error']}")
        
        return result
    
    def test_all_tools(self):
        """测试所有工具"""
        print("=" * 60)
        print("🧪 MCP金融工具全面测试")
        print("=" * 60)
        print(f"测试股票: 山东矿机 ({self.test_symbol})")
        
        # 启动服务器
        if not self.start_mcp_server():
            return
        
        # 获取工具列表
        tools = self.test_tool_list()
        if not tools:
            return
        
        # 定义要测试的工具和参数
        test_cases = [
            # 基础工具
            ("echo", {"text": "测试MCP服务"}),
            ("calculate", {"expression": "2 + 3 * 4"}),
            ("get_time", {}),
            
            # 股票相关工具
            ("get_stock_spot", {"symbol": self.test_symbol}),
            ("get_stock_history", {"symbol": self.test_symbol, "period": "daily"}),
            ("get_stock_financials", {"symbol": self.test_symbol}),
            ("get_stock_valuation", {"symbol": self.test_symbol}),
            ("get_stock_technical_indicators", {"symbol": self.test_symbol}),
            ("get_stock_capital_flow", {"symbol": self.test_symbol}),
            ("get_stock_analyst_ratings", {"symbol": self.test_symbol}),
            ("get_stock_company_info", {"symbol": self.test_symbol}),
            
            # 深度财务分析工具
            ("get_stock_financial_analysis", {"symbol": self.test_symbol}),
            ("get_stock_institute_hold", {"symbol": self.test_symbol}),
            ("get_stock_shareholder_info", {"symbol": self.test_symbol}),
            ("get_stock_lhb_data", {"symbol": self.test_symbol}),
            ("get_stock_hot_rank", {}),
            ("get_stock_news", {"symbol": self.test_symbol}),
            
            # 行业工具
            ("get_industry_news", {"industry": "manufacturing", "days": 7}),
            ("get_policy_support", {"industry": "manufacturing"}),
            ("get_investment_events", {"industry": "manufacturing"}),
            ("get_market_heat", {"industry": "manufacturing"}),
            ("get_industry_overview", {"industry": "manufacturing"}),
            
            # 宏观和市场工具
            ("get_macro_economic_data", {}),
            ("get_northbound_capital", {}),
            
            # 其他金融工具
            ("get_index_data", {"symbol": "000001"}),
            ("get_futures_data", {}),
            ("get_fund_info", {"symbol": "000001"}),  # 示例基金代码
        ]
        
        # 执行测试
        print(f"\n📊 开始测试 {len(test_cases)} 个工具...")
        self.results = {}
        
        for tool_name, params in test_cases:
            result = self.test_tool(tool_name, params)
            self.results[tool_name] = result
        
        # 生成测试报告
        self.generate_report()
        
        # 停止服务器
        self.stop_server()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📈 MCP工具测试结果汇总")
        print("=" * 60)
        
        successful_tools = []
        failed_tools = []
        no_data_tools = []
        
        for tool_name, result in self.results.items():
            if result["success"]:
                if result["data_preview"] and "未找到" not in result["data_preview"]:
                    successful_tools.append(tool_name)
                else:
                    no_data_tools.append(tool_name)
            else:
                failed_tools.append(tool_name)
        
        print(f"📊 总测试数: {len(self.results)}")
        print(f"✅ 成功测试: {len(successful_tools)}")
        print(f"❌ 失败测试: {len(failed_tools)}")
        print(f"⚠️ 无数据测试: {len(no_data_tools)}")
        
        if successful_tools:
            avg_time = sum(r["elapsed_time"] for r in self.results.values() if r["success"]) / len(successful_tools)
            print(f"⏱️ 平均响应时间: {avg_time:.2f}秒")
        
        print(f"\n📋 详细结果:")
        for tool_name, result in self.results.items():
            status = "✅" if result["success"] else "❌"
            if result["success"] and result["data_preview"] and "未找到" in result["data_preview"]:
                status = "⚠️"
            print(f"  {status} {tool_name} - {result['elapsed_time']:.2f}s")
            if result["error"]:
                print(f"     错误: {result['error']}")
        
        # 分析问题工具
        if failed_tools:
            print(f"\n🔧 需要修复的工具 ({len(failed_tools)}):")
            for tool in failed_tools:
                error = self.results[tool]["error"]
                print(f"  - {tool}: {error}")
        
        if no_data_tools:
            print(f"\n📝 无数据但成功的工具 ({len(no_data_tools)}):")
            for tool in no_data_tools:
                print(f"  - {tool}")
    
    def stop_server(self):
        """停止MCP服务器"""
        if self.server_process:
            print(f"\n🛑 停止MCP服务器...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("✅ MCP服务器已停止")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("⚠️ MCP服务器强制停止")

def main():
    """主函数"""
    tester = MCPTester(test_symbol="002526")  # 山东矿机
    tester.test_all_tools()

if __name__ == "__main__":
    main()
