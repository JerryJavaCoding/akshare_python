# Cline Rules Configuration
# 此文件配置Cline在执行Python相关任务时的行为规则

# Python环境配置
# 始终使用项目的虚拟环境执行Python命令
python_environment:
  # 优先使用 .venv 目录
  preferred_venv_path: ".venv"
  # 备选使用 venv 目录  
  fallback_venv_path: "venv"
  # 激活虚拟环境的命令
  activation_command: "source {venv_path}/bin/activate"

# Python命令执行规则
python_execution:
  # 所有Python命令都应该通过虚拟环境执行
  use_venv_for_all_python_commands: true
  
  # 当执行Python脚本时，自动激活虚拟环境
  auto_activate_venv: true
  
  # 当检测到Python依赖缺失时，自动安装
  auto_install_dependencies: true
  
  # 优先使用的Python命令格式
  preferred_python_command: "{venv_path}/bin/python3"
  
  # 备选Python命令格式
  fallback_python_command: "python3 -m venv {venv_path} && {venv_path}/bin/python3"

# 项目特定配置
project_specific:
  # 项目根目录
  project_root: "/Users/jerry/code/akshare_python"
  
  # 主要依赖文件
  dependency_files:
    - "pyproject.toml"
    - "requirements.txt"
  
  # 测试命令
  test_commands:
    - "pytest"
    - "python -m pytest"
    - "python3 -m pytest"

# 命令执行规则
command_rules:
  # 当执行Python相关命令时，自动切换到项目根目录
  auto_cd_to_project_root: true
  
  # 当执行pip install时，确保使用虚拟环境的pip
  use_venv_pip: true
  
  # 当执行Python脚本时，自动设置PYTHONPATH
  set_pythonpath: true
  
  # Python路径设置
  pythonpath: "src"

# 错误处理
error_handling:
  # 当虚拟环境不存在时，自动创建
  auto_create_venv: true
  
  # 当依赖缺失时，自动安装
  auto_install_missing_deps: true
  
  # 当Python命令失败时，提供修复建议
  provide_fix_suggestions: true

# 示例命令映射
command_mappings:
  # 原始命令 -> 使用venv的命令
  "python": "{venv_path}/bin/python3"
  "python3": "{venv_path}/bin/python3"
  "pip": "{venv_path}/bin/pip"
  "pip3": "{venv_path}/bin/pip3"
  "pytest": "{venv_path}/bin/pytest"
