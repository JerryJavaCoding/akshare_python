#!/usr/bin/env python3
"""
测试修复后的MCP工具
"""

import subprocess
import time
import json
import sys

def test_specific_tools():
    """测试特定的问题工具"""
    print("🧪 测试修复后的MCP工具...")
    
    # 启动MCP服务器
    server_process = subprocess.Popen(
        [sys.executable, "mcp_services/finance_server/finance_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    print("✅ MCP服务器已启动")
    time.sleep(2)
    
    try:
        # 测试有问题的工具
        problem_tools = [
            "get_stock_institute_hold",
            "get_stock_shareholder_info",
            "get_stock_lhb_data",
            "get_stock_hot_rank",
            "get_stock_news",
            "get_macro_economic_data",
            "get_northbound_capital"
        ]
        
        for tool_name in problem_tools:
            print(f"\n🔍 测试: {tool_name}")
            
            # 构建请求参数
            params = {}
            if tool_name in ["get_stock_institute_hold", "get_stock_shareholder_info", "get_stock_news"]:
                params = {"symbol": "002526"}
            elif tool_name == "get_stock_lhb_data":
                params = {"symbol": ""}  # 测试空参数
            
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": params
                }
            }
            
            # 发送请求
            server_process.stdin.write(json.dumps(request) + "\n")
            server_process.stdin.flush()
            
            # 读取响应
            response_line = server_process.stdout.readline().strip()
            if response_line:
                response_data = json.loads(response_line)
                if "result" in response_data:
                    print(f"✅ {tool_name} - 成功")
                    if "content" in response_data["result"] and response_data["result"]["content"]:
                        content_text = response_data["result"]["content"][0].get("text", "")
                        preview = content_text[:100] + "..." if len(content_text) > 100 else content_text
                        print(f"   数据预览: {preview}")
                else:
                    print(f"❌ {tool_name} - 失败: {response_data.get('error', '未知错误')}")
            else:
                print(f"❌ {tool_name} - 无响应")
                
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
    
    finally:
        # 清理服务器进程
        print("\n🛑 停止MCP服务器...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
            print("✅ MCP服务器已停止")
        except subprocess.TimeoutExpired:
            server_process.kill()
            print("⚠️ MCP服务器强制停止")

if __name__ == "__main__":
    test_specific_tools()
