#!/usr/bin/env python3
"""
简单测试MCP服务器连接
"""

import subprocess
import time
import json
import sys

def test_mcp_connection():
    """测试MCP服务器连接"""
    print("🧪 测试MCP服务器连接...")
    
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
    time.sleep(2)  # 等待服务器初始化
    
    try:
        # 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 发送初始化请求...")
        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        
        # 读取初始化响应
        init_response = server_process.stdout.readline().strip()
        print(f"📥 收到初始化响应: {init_response}")
        
        if init_response:
            init_data = json.loads(init_response)
            if "result" in init_data:
                print("✅ 初始化成功")
                
                # 发送工具列表请求
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
                
                print("📤 发送工具列表请求...")
                server_process.stdin.write(json.dumps(tools_request) + "\n")
                server_process.stdin.flush()
                
                # 读取工具列表响应
                tools_response = server_process.stdout.readline().strip()
                print(f"📥 收到工具列表响应: {tools_response}")
                
                if tools_response:
                    tools_data = json.loads(tools_response)
                    if "result" in tools_data and "tools" in tools_data["result"]:
                        tools = tools_data["result"]["tools"]
                        print(f"✅ 成功获取到 {len(tools)} 个工具")
                        
                        # 测试一个简单的工具
                        echo_request = {
                            "jsonrpc": "2.0",
                            "id": 3,
                            "method": "tools/call",
                            "params": {
                                "name": "echo",
                                "arguments": {"text": "Hello MCP!"}
                            }
                        }
                        
                        print("📤 发送echo工具请求...")
                        server_process.stdin.write(json.dumps(echo_request) + "\n")
                        server_process.stdin.flush()
                        
                        # 读取echo响应
                        echo_response = server_process.stdout.readline().strip()
                        print(f"📥 收到echo响应: {echo_response}")
                        
                        if echo_response:
                            echo_data = json.loads(echo_response)
                            if "result" in echo_data:
                                print("✅ echo工具测试成功")
                                return True
                            else:
                                print(f"❌ echo工具失败: {echo_data.get('error', '未知错误')}")
                        else:
                            print("❌ 未收到echo响应")
                    else:
                        print("❌ 获取工具列表失败")
                else:
                    print("❌ 未收到工具列表响应")
            else:
                print(f"❌ 初始化失败: {init_data.get('error', '未知错误')}")
        else:
            print("❌ 未收到初始化响应")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
    
    finally:
        # 清理服务器进程
        print("🛑 停止MCP服务器...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
            print("✅ MCP服务器已停止")
        except subprocess.TimeoutExpired:
            server_process.kill()
            print("⚠️ MCP服务器强制停止")
    
    return False

if __name__ == "__main__":
    success = test_mcp_connection()
    if success:
        print("\n🎉 MCP服务器连接测试成功！")
        print("💡 现在可以在Cline中配置MCP服务器了")
    else:
        print("\n💥 MCP服务器连接测试失败")
        print("🔧 请检查MCP服务器实现")
