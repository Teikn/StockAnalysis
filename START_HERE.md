# 🚀 快速启动卡

## 一句话启动

### macOS
```bash
双击 run_app.command
```

### Windows  
```bash
双击 run_app.bat
```

### 通用
```bash
python3 run_app.py
```

---

## 自动完成的事项

启动脚本会自动执行：

1. ✅ 检查虚拟环境
2. ✅ 激活虚拟环境
3. ✅ 检查依赖包
4. ✅ 启动 Streamlit
5. ✅ 打开浏览器 → http://localhost:8501

---

## 应用入口

**浏览器访问：** http://localhost:8501

---

## 6个功能页面

```
➕ 录入交易      📥 导入CSV
📃 交易列表      📦 持仓汇总
📊 Dashboard    💰 价格/汇率
```

---

## 数据位置

**数据库：** `stocktool/portfolio.db`

---

## 停止应用

按 `Ctrl+C` 在终端中

---

## 文件位置参考

```
项目根目录: /Users/tin/git/StockAnalysis

启动脚本:
  • run_app.command (macOS)
  • run_app.bat (Windows)
  • run_app.py (通用)

主要文件:
  • stocktool/app.py (Streamlit 应用)
  • stocktool/db.py (数据库管理)
  • stocktool/portfolio.db (数据库文件)

虚拟环境:
  • .venv/ (环境目录)
```

---

## 文档链接

- **SETUP_COMPLETE.md** - 设置完成说明 ⭐ 首先读这个
- **LAUNCH_GUIDE.md** - 详细启动指南
- **QUICK_START.md** - 应用使用快速参考
- **README.md** - 完整用户手册
- **.github/copilot-instructions.md** - 开发指南

---

**准备好了？双击启动应用！** 🎉
