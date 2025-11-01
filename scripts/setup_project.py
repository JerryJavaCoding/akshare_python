#!/usr/bin/env python3
"""
项目安装和配置脚本
自动化安装依赖、创建虚拟环境、配置项目
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


class ProjectSetup:
    """项目安装配置类"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / ".venv"
        self.system = platform.system().lower()
        
    def print_header(self, message):
        """打印标题"""
        print("\n" + "=" * 60)
        print(f"🤖 {message}")
        print("=" * 60)
    
    def check_python_version(self):
        """检查Python版本"""
        self.print_header("检查Python版本")
        
        version = sys.version_info
        print(f"当前Python版本: {sys.version}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ 错误: 需要Python 3.8或更高版本")
            return False
        
        print("✅ Python版本符合要求")
        return True
    
    def create_venv(self):
        """创建虚拟环境"""
        self.print_header("创建虚拟环境")
        
        if self.venv_path.exists():
            print(f"✅ 虚拟环境已存在: {self.venv_path}")
            return True
        
        try:
            print(f"创建虚拟环境到: {self.venv_path}")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
            print("✅ 虚拟环境创建成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 虚拟环境创建失败: {e}")
            return False
    
    def get_venv_python(self):
        """获取虚拟环境Python路径"""
        if self.system == "windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def get_venv_pip(self):
        """获取虚拟环境pip路径"""
        if self.system == "windows":
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
    
    def install_dependencies(self):
        """安装项目依赖"""
        self.print_header("安装项目依赖")
        
        venv_pip = self.get_venv_pip()
        if not venv_pip.exists():
            print("❌ 虚拟环境pip不存在，请先创建虚拟环境")
            return False
        
        try:
            # 安装基础依赖
            print("安装基础依赖...")
            subprocess.run([str(venv_pip), "install", "-e", "."], check=True)
            
            # 安装开发依赖
            print("安装开发依赖...")
            subprocess.run([str(venv_pip), "install", "-e", ".[dev]"], check=True)
            
            print("✅ 依赖安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False
    
    def setup_environment(self):
        """设置环境变量"""
        self.print_header("设置环境变量")
        
        # 创建.env文件示例
        env_file = self.project_root / ".env.example"
        env_content = """# MCP项目环境配置

# 金融服务配置
FINANCE_API_KEY=your_api_key_here
FINANCE_API_SECRET=your_api_secret_here

# 数据库配置
DATABASE_URL=sqlite:///data/finance.db

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 网络配置
REQUEST_TIMEOUT=30
MAX_RETRIES=3
"""
        
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            print(f"✅ 环境配置文件示例已创建: {env_file}")
            
            # 提示用户复制配置文件
            print("\n📝 请复制 .env.example 为 .env 并配置您的环境变量:")
            print(f"  cp {env_file} {self.project_root / '.env'}")
            
        except Exception as e:
            print(f"❌ 创建环境配置文件失败: {e}")
    
    def create_directories(self):
        """创建必要的目录结构"""
        self.print_header("创建目录结构")
        
        directories = [
            "data",
            "logs", 
            "output",
            "temp"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"✅ 创建目录: {directory}")
            except Exception as e:
                print(f"❌ 创建目录失败 {directory}: {e}")
    
    def run_tests(self):
        """运行测试验证安装"""
        self.print_header("运行测试验证安装")
        
        venv_python = self.get_venv_python()
        if not venv_python.exists():
            print("❌ 虚拟环境Python不存在")
            return False
        
        try:
            # 运行MCP服务测试
            print("运行MCP服务测试...")
            test_script = self.project_root / "scripts" / "test_mcp_service.py"
            result = subprocess.run([str(venv_python), str(test_script)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ MCP服务测试通过")
                return True
            else:
                print("❌ MCP服务测试失败")
                print(f"错误输出: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 测试运行失败: {e}")
            return False
    
    def print_usage_instructions(self):
        """打印使用说明"""
        self.print_header("使用说明")
        
        venv_python = self.get_venv_python()
        
        print("🎯 项目已配置完成！以下是如何使用：")
        print("\n1. 激活虚拟环境:")
        if self.system == "windows":
            print(f"   {self.venv_path / 'Scripts' / 'activate'}")
        else:
            print(f"   source {self.venv_path / 'bin' / 'activate'}")
        
        print("\n2. 启动MCP服务:")
        print(f"   {venv_python} scripts/start_mcp_server.py")
        
        print("\n3. 测试MCP服务:")
        print(f"   {venv_python} scripts/test_mcp_service.py")
        
        print("\n4. 运行爬虫服务:")
        print(f"   {venv_python} src/main/crawler_services/red_ring/main.py")
        
        print("\n📚 更多信息请查看 README.md")
    
    def run_setup(self):
        """运行完整的安装配置流程"""
        self.print_header("开始项目安装配置")
        
        print(f"项目根目录: {self.project_root}")
        print(f"操作系统: {platform.system()} {platform.release()}")
        
        # 执行安装步骤
        steps = [
            ("检查Python版本", self.check_python_version),
            ("创建虚拟环境", self.create_venv),
            ("安装依赖", self.install_dependencies),
            ("创建目录结构", self.create_directories),
            ("设置环境变量", self.setup_environment),
            ("运行测试验证", self.run_tests)
        ]
        
        success = True
        for step_name, step_func in steps:
            if not step_func():
                print(f"❌ {step_name}失败")
                success = False
                break
            else:
                print(f"✅ {step_name}完成")
        
        if success:
            self.print_usage_instructions()
            print("\n🎉 项目安装配置完成！")
        else:
            print("\n❌ 项目安装配置失败，请检查错误信息")
        
        return success


def main():
    """主函数"""
    setup = ProjectSetup()
    success = setup.run_setup()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
