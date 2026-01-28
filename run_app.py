#!/usr/bin/env python3
"""
StockAnalysis 启动脚本 - 跨平台

这个脚本可以在 Mac/Linux/Windows 上运行
双击或在终端执行即可启动应用

使用方法：
  python3 run_app.py
  
或在 Mac 上双击此文件：
  右键 -> 打开方式 -> Python
"""

import subprocess
import sys
import os
from pathlib import Path

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent.absolute()
os.chdir(SCRIPT_DIR)

def create_venv():
    """创建虚拟环境"""
    venv_path = SCRIPT_DIR / ".venv"
    if venv_path.exists():
        return True
    
    print("⚠️  虚拟环境不存在，正在创建...")
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✅ 虚拟环境创建成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ 虚拟环境创建失败")
        return False

def install_dependencies():
    """安装依赖"""
    print("🔍 检查依赖...")
    
    # 确定 pip 命令
    if sys.platform == "win32":
        pip_cmd = [str(SCRIPT_DIR / ".venv" / "Scripts" / "pip")]
    else:
        pip_cmd = [str(SCRIPT_DIR / ".venv" / "bin" / "pip")]
    
    packages = ["streamlit", "pandas", "numpy", "yfinance"]
    
    try:
        subprocess.run(
            pip_cmd + ["install", "-q"] + packages,
            check=False,
            capture_output=True
        )
        print("✅ 依赖检查完成")
        return True
    except Exception as e:
        print(f"⚠️  依赖安装可能有问题: {e}")
        return True  # 继续运行

def get_python_executable():
    """获取虚拟环境中的 Python 可执行文件"""
    if sys.platform == "win32":
        return str(SCRIPT_DIR / ".venv" / "Scripts" / "python.exe")
    else:
        return str(SCRIPT_DIR / ".venv" / "bin" / "python")

def main():
    """主函数"""
    print()
    print("╔════════════════════════════════════════════╗")
    print("║     📊 StockAnalysis 启动程序              ║")
    print("╚════════════════════════════════════════════╝")
    print()
    
    # 第一步：创建虚拟环境
    if not create_venv():
        print("\n❌ 启动失败：无法创建虚拟环境")
        input("按 Enter 退出...")
        sys.exit(1)
    
    # 第二步：安装依赖
    install_dependencies()
    
    # 第三步：启动应用
    print()
    print("╔════════════════════════════════════════════╗")
    print("║     🚀 StockAnalysis 正在启动...          ║")
    print("╚════════════════════════════════════════════╝")
    print()
    print("📱 应用将在浏览器打开: http://localhost:8501")
    print("💡 提示: 按 Ctrl+C 可以停止应用")
    print()
    
    python_exe = get_python_executable()
    app_file = SCRIPT_DIR / "stocktool" / "app.py"
    
    try:
        subprocess.run(
            [python_exe, "-m", "streamlit", "run", str(app_file), "--logger.level=error"],
            cwd=str(SCRIPT_DIR)
        )
    except KeyboardInterrupt:
        print("\n\n👋 应用已关闭")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        input("按 Enter 退出...")

if __name__ == "__main__":
    main()
