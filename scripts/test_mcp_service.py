#!/usr/bin/env python3
"""
MCP服务测试脚本
用于测试MCP服务的功能和可用性
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main.mcp_services.finance_server.finance_server import FixedMCPServer


async def test_tool_list():
    """测试工具列表功能"""
    print("🔧 测试工具列表...")
    server = FixedMCPServer()
    
    # 模拟tools/list请求
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    response = await server.process_message(json.dumps(request))
    response_data = json.loads(response)
    
    if "result" in response_data and "tools" in response_data["result"]:
        tools = response_data["result"]["tools"]
        print(f"✅ 成功获取 {len(tools)} 个工具")
        
        # 显示前5个工具作为示例
        print("\n📋 工具列表 (前5个):")
        for i, tool in enumerate(tools[:5], 1):
            print(f"  {i}. {tool['name']}: {tool['description']}")
        
        if len(tools) > 5:
            print(f"  ... 还有 {len(tools) - 5} 个工具")
        
        return True
    else:
        print("❌ 获取工具列表失败")
        print(f"响应: {response_data}")
        return False


async def test_echo_tool():
    """测试echo工具"""
    print("\n🔊 测试echo工具...")
    server = FixedMCPServer()
    
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "echo",
            "arguments": {
                "text": "Hello, MCP Server!"
            }
        }
    }
    
    response = await server.process_message(json.dumps(request))
    response_data = json.loads(response)
    
    if "result" in response_data and "content" in response_data["result"]:
        content = response_data["result"]["content"]
        if content and content[0]["text"] == "Hello, MCP Server!":
            print("✅ echo工具测试成功")
            return True
        else:
            print("❌ echo工具返回内容不匹配")
            print(f"期望: Hello, MCP Server!")
            print(f"实际: {content[0]['text']}")
            return False
    else:
        print("❌ echo工具调用失败")
        print(f"响应: {response_data}")
        return False


async def test_calculate_tool():
    """测试计算工具"""
    print("\n🧮 测试计算工具...")
    server = FixedMCPServer()
    
    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "calculate",
            "arguments": {
                "expression": "2 + 3 * 4"
            }
        }
    }
    
    response = await server.process_message(json.dumps(request))
    response_data = json.loads(response)
    
    if "result" in response_data and "content" in response_data["result"]:
        content = response_data["result"]["content"]
        if "14" in content[0]["text"]:
            print("✅ 计算工具测试成功")
            return True
        else:
            print("❌ 计算工具结果不正确")
            print(f"响应: {content[0]['text']}")
            return False
    else:
        print("❌ 计算工具调用失败")
        print(f"响应: {response_data}")
        return False


async def test_finance_tools():
    """测试金融工具"""
    print("\n📈 测试金融工具...")
    server = FixedMCPServer()
    
    # 测试获取股票实时行情
    request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_stock_spot",
            "arguments": {
                "symbol": "000001"
            }
        }
    }
    
    response = await server.process_message(json.dumps(request))
    response_data = json.loads(response)
    
    if "result" in response_data and "content" in response_data["result"]:
        content = response_data["result"]["content"]
        print("✅ 股票实时行情工具测试成功")
        print(f"📊 返回数据长度: {len(content[0]['text'])} 字符")
        return True
    else:
        print("❌ 股票实时行情工具调用失败")
        print(f"响应: {response_data}")
        return False


async def test_industry_tools():
    """测试行业分析工具"""
    print("\n🏭 测试行业分析工具...")
    server = FixedMCPServer()
    
    # 测试获取行业新闻
    request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "get_industry_news",
            "arguments": {
                "industry": "technology",
                "days": 3
            }
        }
    }
    
    response = await server.process_message(json.dumps(request))
    response_data = json.loads(response)
    
    if "result" in response_data and "content" in response_data["result"]:
        content = response_data["result"]["content"]
        print("✅ 行业新闻工具测试成功")
        print(f"📰 返回数据长度: {len(content[0]['text'])} 字符")
        return True
    else:
        print("❌ 行业新闻工具调用失败")
        print(f"响应: {response_data}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("🧪 开始MCP服务测试...")
    print("=" * 50)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(await test_tool_list())
    test_results.append(await test_echo_tool())
    test_results.append(await test_calculate_tool())
    test_results.append(await test_finance_tools())
    test_results.append(await test_industry_tools())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！MCP服务运行正常")
        return True
    else:
        print("⚠️  部分测试失败，请检查服务配置")
        return False


def main():
    """主函数"""
    print("🤖 MCP服务测试脚本")
    print("=" * 50)
    
    # 检查项目根目录
    if not (project_root / "src").exists():
        print("❌ 错误: 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 运行测试
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n✅ MCP服务测试完成，服务可用")
        sys.exit(0)
    else:
        print("\n❌ MCP服务测试完成，发现问题")
        sys.exit(1)


if __name__ == "__main__":
    main()
