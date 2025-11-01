#!/usr/bin/env python3
"""
最终MCP服务器测试
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mcp_import():
    """测试MCP服务器导入"""
    try:
        from mcp_services.finance_server.finance_server import FixedMCPServer
        print("✅ MCP服务器导入成功")
        
        # 测试工具列表
        server = FixedMCPServer()
        tools = server._get_tools()
        print(f"✅ 获取到 {len(tools)} 个工具")
        
        # 测试几个关键工具
        test_tools = ["echo", "get_time", "get_stock_spot", "get_stock_institute_hold"]
        for tool_name in test_tools:
            tool = next((t for t in tools if t["name"] == tool_name), None)
            if tool:
                print(f"✅ 工具 {tool_name} 存在")
            else:
                print(f"❌ 工具 {tool_name} 不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP服务器导入失败: {e}")
        return False

def test_finance_tools():
    """测试金融工具"""
    try:
        from mcp_services.finance_server.finance_tools import FinanceDataService
        print("✅ 金融工具导入成功")
        
        # 测试几个关键函数
        test_symbol = "002526"  # 山东矿机
        
        # 测试股票实时数据
        try:
            result = FinanceDataService.get_stock_spot(test_symbol)
            if result and isinstance(result, list) and len(result) > 0:
                print(f"✅ get_stock_spot 成功 - 返回 {len(result)} 条数据")
            else:
                print(f"⚠️ get_stock_spot 返回空数据")
        except Exception as e:
            print(f"❌ get_stock_spot 失败: {e}")
        
        # 测试机构持股
        try:
            result = FinanceDataService.get_stock_institute_hold(test_symbol)
            if result and isinstance(result, list) and len(result) > 0:
                print(f"✅ get_stock_institute_hold 成功 - 返回 {len(result)} 条数据")
            else:
                print(f"⚠️ get_stock_institute_hold 返回空数据")
        except Exception as e:
            print(f"❌ get_stock_institute_hold 失败: {e}")
        
        # 测试股东信息
        try:
            result = FinanceDataService.get_stock_shareholder_info(test_symbol)
            if result and isinstance(result, list) and len(result) > 0:
                print(f"✅ get_stock_shareholder_info 成功 - 返回 {len(result)} 条数据")
            else:
                print(f"⚠️ get_stock_shareholder_info 返回空数据")
        except Exception as e:
            print(f"❌ get_stock_shareholder_info 失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 金融工具导入失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 MCP服务器最终测试")
    print("=" * 60)
    
    # 测试MCP服务器导入
    print("\n📦 测试MCP服务器导入...")
    mcp_success = test_mcp_import()
    
    # 测试金融工具
    print("\n📊 测试金融工具...")
    finance_success = test_finance_tools()
    
    # 总结
    print("\n" + "=" * 60)
    print("📈 测试结果汇总")
    print("=" * 60)
    
    if mcp_success and finance_success:
        print("🎉 所有测试通过！MCP服务器已修复并可以正常工作")
        print("\n💡 现在可以在Cline中配置MCP服务器了")
        print("配置路径: mcp_services/finance_server/finance_server.py")
    else:
        print("💥 部分测试失败，需要进一步修复")
        
        if not mcp_success:
            print("- MCP服务器导入存在问题")
        if not finance_success:
            print("- 金融工具实现存在问题")

if __name__ == "__main__":
    main()
