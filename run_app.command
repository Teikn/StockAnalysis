#!/bin/bash

# StockAnalysis - macOS 启动脚本
# 双击此文件即可启动应用

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "⚠️  虚拟环境不存在，正在创建..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 检查依赖
echo "🔍 检查依赖..."
pip install -q streamlit pandas numpy yfinance 2>/dev/null

# 启动应用
echo ""
echo "╔════════════════════════════════════════════╗"
echo "║     🚀 StockAnalysis 正在启动...          ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "📱 应用将在浏览器打开: http://localhost:8501"
echo "💡 提示: 按 Ctrl+C 可以停止应用"
echo ""

# 启动 Streamlit
streamlit run stocktool/app.py --logger.level=error
