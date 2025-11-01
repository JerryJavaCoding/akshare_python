#!/usr/bin/env python3
"""Test script for integrated MCP server."""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.mcp_server.finance_server import FixedMCPServer, THSDataService

def test_integrated_server():
    """Test the integrated MCP server functionality."""
    print("=== 测试整合后的MCP服务器 ===\n")
    
    # 创建服务器实例
    server = FixedMCPServer()
    
    # 测试工具列表
    print("1. 测试工具列表...")
    tools = server._get_tools()
    print(f"可用工具数量: {len(tools)}")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    
    print("\n2. 测试同花顺数据服务...")
    
    # 测试行业新闻
    print("\n3. 测试获取新能源行业新闻...")
    news_result = THSDataService.get_industry_news("new_energy")
    for content in news_result:
        print(content.text)
        print("-" * 50)
    
    # 测试市场热度
    print("\n4. 测试获取人工智能行业市场热度...")
    heat_result = THSDataService.get_market_heat("ai")
    for content in heat_result:
        print(content.text)
        print("-" * 50)
    
    # 测试行业概览
    print("\n5. 测试获取半导体行业概览...")
    overview_result = THSDataService.get_industry_overview("semiconductor")
    for content in overview_result:
        print(content.text)
        print("-" * 50)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_integrated_server()
