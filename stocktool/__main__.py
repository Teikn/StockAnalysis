"""
StockAnalysis CLI entry point (deprecated - use Streamlit instead)

Legacy CLI entry point. Recommend running via Streamlit:
  streamlit run stocktool/app.py

This entry point is kept for backwards compatibility.
"""

import subprocess
import sys

if __name__ == "__main__":
    print("📝 StockAnalysis - 本地投资记录工具")
    print("=" * 50)
    print("\n✨ 推荐用法（Streamlit Web 界面）:")
    print("   streamlit run stocktool/app.py")
    print("\n💬 或者执行: python -m stocktool run-app")
    print("\n" + "=" * 50)
    
    # Try to run Streamlit if 'run-app' is passed
    if len(sys.argv) > 1 and sys.argv[1] == "run-app":
        print("\n🚀 启动 Streamlit 应用...")
        subprocess.run(
            ["streamlit", "run", "stocktool/app.py"],
            cwd="/".join(__file__.split("/")[:-2])
        )

