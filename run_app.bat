@echo off
REM StockAnalysis - Windows 启动脚本
REM 双击此文件即可启动应用

cd /d "%~dp0"

REM 检查虚拟环境
if not exist ".venv" (
    echo ⚠️  虚拟环境不存在，正在创建...
    python -m venv .venv
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 检查依赖
echo 🔍 检查依赖...
pip install -q streamlit pandas numpy yfinance 2>nul

REM 启动应用
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║     🚀 StockAnalysis 正在启动...          ║
echo ╚════════════════════════════════════════════╝
echo.
echo 📱 应用将在浏览器打开: http://localhost:8501
echo 💡 提示: 按 Ctrl+C 可以停止应用
echo.

REM 启动 Streamlit
streamlit run stocktool/app.py --logger.level=error

pause
