#!/usr/bin/env python3
"""
MCP服务器通用启动脚本
提供统一的MCP服务启动入口，支持多种配置选项
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main.mcp_services.finance_server.finance_server import FixedMCPServer


def setup_environment():
    """设置运行环境"""
    # 确保在项目根目录运行
    os.chdir(project_root)
    print(f"工作目录: {os.getcwd()}")
    
    # 检查虚拟环境
    venv_path = project_root / ".venv"
    if venv_path.exists():
        print(f"检测到虚拟环境: {venv_path}")
    else:
        print("警告: 未检测到虚拟环境，建议使用虚拟环境运行")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="MCP服务器启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python scripts/start_mcp_server.py                    # 默认启动金融服务
  python scripts/start_mcp_server.py --service finance  # 指定启动金融服务
  python scripts/start_mcp_server.py --debug            # 启用调试模式
        """
    )
    
    parser.add_argument(
        "--service",
        choices=["finance"],
        default="finance",
        help="选择要启动的MCP服务 (默认: finance)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式，输出详细日志"
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="服务器监听地址 (默认: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器监听端口 (默认: 8000)"
    )
    
    return parser.parse_args()


async def start_finance_server(debug=False):
    """启动金融服务"""
    print("🚀 启动MCP金融服务...")
    
    if debug:
        print("🔧 调试模式已启用")
        print("📊 可用工具列表:")
        server = FixedMCPServer()
        for tool in server.tools:
            print(f"  - {tool['name']}: {tool['description']}")
    
    try:
        from src.main.mcp_services.finance_server.finance_server import main
        await main()
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        if debug:
            import traceback
            traceback.print_exc()


async def main():
    """主函数"""
    args = parse_arguments()
    
    print("=" * 50)
    print("🤖 MCP服务器启动器")
    print("=" * 50)
    
    setup_environment()
    
    print(f"📡 服务类型: {args.service}")
    print(f"🐛 调试模式: {'启用' if args.debug else '禁用'}")
    
    try:
        if args.service == "finance":
            await start_finance_server(args.debug)
        else:
            print(f"❌ 不支持的服务类型: {args.service}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
