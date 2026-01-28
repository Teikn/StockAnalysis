# 🚀 StockAnalysis 启动指南

## 📋 环境已准备完毕！

虚拟环境 `.venv` 和所有依赖已安装完成。

---

## 🎯 启动应用（三种方式）

### 方式一：双击启动（推荐 macOS）

**文件：** `run_app.command`

1. 打开 Finder
2. 找到项目文件夹中的 `run_app.command`
3. **双击**即可启动应用

✅ 自动打开浏览器进入 http://localhost:8501

---

### 方式二：双击启动（Windows）

**文件：** `run_app.bat`

1. 打开文件管理器
2. 找到项目文件夹中的 `run_app.bat`
3. **双击**即可启动应用

✅ 自动打开浏览器进入 http://localhost:8501

---

### 方式三：Python 脚本启动（Mac/Linux/Windows）

**文件：** `run_app.py`

```bash
# 方式 A：在终端中运行
python3 run_app.py

# 方式 B：双击（需要右键 -> 打开方式 -> Python）
```

✅ 自动打开浏览器进入 http://localhost:8501

---

### 方式四：手动启动（终端）

```bash
# 1. 进入项目目录
cd /Users/tin/git/StockAnalysis

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 启动应用
streamlit run stocktool/app.py
```

---

## 📱 应用启动后

1. **浏览器自动打开** → http://localhost:8501
2. **看到 Streamlit 界面** 说明启动成功 ✅
3. **侧边栏有 6 个功能页面**

---

## 🎨 功能页面

在应用启动后，你会看到侧边栏有这 6 个页面：

| 图标 | 页面名称 | 功能 |
|------|--------|------|
| ➕ | 录入交易 | 手动输入交易 |
| 📥 | 导入CSV | 批量导入交易 |
| 📃 | 交易列表 | 查看所有交易 |
| 📦 | 持仓汇总 | 查看当前持仓 |
| 📊 | Dashboard | 查看总资产和收益 |
| 💰 | 价格/汇率 | 维护价格数据 |

---

## ⚙️ 系统要求

- **Mac:** Python 3.8+（已配置）
- **Windows:** Python 3.8+（已配置）
- **浏览器:** Chrome/Safari/Firefox/Edge

---

## 🔧 环境信息

```
项目位置:    /Users/tin/git/StockAnalysis
虚拟环境:    .venv/
Python:     3.x
Streamlit:  ✅ 已安装
Pandas:     ✅ 已安装
NumPy:      ✅ 已安装
YFinance:   ✅ 已安装（可选）
```

---

## ❓ 常见问题

### Q: 应用无法启动？
**A:** 
1. 确保在项目根目录
2. 检查 `stocktool/app.py` 是否存在
3. 尝试手动启动：`source .venv/bin/activate && streamlit run stocktool/app.py`

### Q: 浏览器没有自动打开？
**A:** 手动访问 http://localhost:8501

### Q: 显示"Module not found"？
**A:** 运行此命令重新安装依赖：
```bash
source .venv/bin/activate
pip install streamlit pandas numpy yfinance
```

### Q: 如何关闭应用？
**A:** 在终端中按 `Ctrl+C`

---

## 📚 参考文档

- **快速入门:** `QUICK_START.md`
- **完整手册:** `README.md`
- **开发指南:** `.github/copilot-instructions.md`
- **迁移说明:** `MIGRATION.md`

---

## ✨ 快速操作

### 第一次使用

1. 双击 `run_app.command`（Mac）或 `run_app.bat`（Windows）
2. 等待应用启动
3. 进入 **➕ 录入交易** 页面
4. 记录你的第一笔交易

### 日常使用

**启动应用：**
```bash
python3 run_app.py
```

**或直接双击：**
- Mac: `run_app.command`
- Windows: `run_app.bat`

---

## 🎉 准备好了！

立即启动应用，开始追踪你的投资吧！

**推荐：双击 `run_app.command` (Mac) 或 `run_app.bat` (Windows)**

祝您使用愉快！ 🚀
