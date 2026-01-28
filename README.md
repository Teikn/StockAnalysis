# 📒 Stock Journal - 本地投资追踪工具

[![Status](https://img.shields.io/badge/status-ready-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-Personal-lightgrey)]()

本地 Python 投资记录工具 - **Streamlit Web UI** + **SQLite 本地数据库** + **pandas 数据分析**。

用来记录交易、追踪持仓、计算成本和损益。所有数据保存在本地，完全隐私。

## ✨ 功能特性

- 📝 **单笔交易录入**：支持买/卖、手续费、多币种、汇率换算
- 📥 **批量 CSV 导入**：灵活的列映射，快速导入券商交易记录
- 📃 **交易列表查询**：按代码筛选、时间排序、完整历史
- 📦 **持仓汇总分析**：持股数量、均成本、成本基数、已实现/未实现损益（JPY 口径）
- 📊 **Dashboard 概览**：总资产、总收益、收益率、按 Ticker 分布
- 💰 **价格数据管理**：手动录入或自动拉取（yfinance）最新价格用于浮动盈亏
- 🔐 **本地存储**：所有数据存放于 SQLite，完全隐私，不上传云端
- 🌍 **多币种支持**：JPY、USD、EUR 等，自动转换为 JPY 基准计算

## 🚀 快速开始

### ⚡️ 最快启动方式（推荐）

**macOS 用户**：双击 `run_app.command`  
**Windows 用户**：双击 `run_app.bat`  
**其他用户**：运行 `python3 run_app.py`

一键启动，自动完成虚拟环境检查、依赖安装、浏览器打开。

### 🔧 手动启动

```bash
# 1. 创建虚拟环境（首次）
python3 -m venv .venv

# 2. 激活虚拟环境
source .venv/bin/activate          # macOS/Linux
# 或
.venv\Scripts\activate             # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行应用
streamlit run stocktool/app.py
```

浏览器会自动打开 **http://localhost:8501**

### 📖 开始使用

应用启动后，侧边栏显示 6 个功能页面：

1. **➕ 录入交易** - 手动输入单笔交易（日期、代码、方向、数量、价格、币种、手续费、汇率、备注）
2. **📥 导入CSV** - 从券商导出 CSV，灵活列映射，批量导入
3. **📃 交易列表** - 查看全部交易，支持 Ticker 筛选、时间排序
4. **📦 持仓汇总** - 显示当前持仓、成本、已实现/未实现损益（移动平均成本法）
5. **📊 Dashboard** - 总资产、收益率、按 Ticker 的已实现损益分布
6. **💰 价格/汇率** - 维护最新价格（手动或自动拉取）用于浮动盈亏计算

详细使用说明见 [QUICK_START.md](QUICK_START.md)

## 💾 数据库

| 项目 | 说明 |
|------|------|
| 位置 | `stocktool/portfolio.db`（SQLite 文件） |
| 初始化 | 首次运行 app.py 时自动创建表和索引 |
| 备份 | 数据库文件位于 `stocktool/` 目录，建议定期备份 |
| 重置 | 删除 `portfolio.db` 文件，重新启动应用即可重新初始化 |

### 数据库架构

**trades 表**：交易记录
```
id | trade_date | ticker | side | quantity | price | currency | fees | fx_to_jpy | note
```

**prices 表**：最新价格数据
```
ticker | price | currency | fx_to_jpy | asof
```

详见 [.github/copilot-instructions.md](.github/copilot-instructions.md) 的"数据模型"章节

## 📁 项目结构

```
StockAnalysis/
├── stocktool/                  # 应用主包
│   ├── app.py                 # Streamlit 应用主入口（UI + 业务逻辑 564 行）
│   ├── db.py                  # SQLite 数据库管理层（112 行）
│   ├── __init__.py
│   ├── __main__.py
│   ├── models.py
│   ├── portfolio.db           # SQLite 数据库文件（首次运行时生成）
│   ├── cli.py                 # 旧 CLI（已弃用）
│   └── services/              # 业务逻辑层
│       ├── portfolio.py
│       └── trades.py
│
├── tests/                      # 单元测试
│   └── test_portfolio.py
│
├── .streamlit/config.toml      # Streamlit 配置
├── .github/copilot-instructions.md  # AI 开发指南（284 行）
│
├── 📖 文档文件
│   ├── README.md              # 本文件（用户手册）
│   ├── QUICK_START.md         # 快速使用指南
│   ├── FEATURES.md            # 功能清单（含版本历史）
│   ├── SETUP_COMPLETE.md      # 安装完成说明
│   ├── LAUNCH_GUIDE.md        # 启动方式详解
│   ├── START_HERE.md          # 快速参考卡
│   ├── MIGRATION.md           # 架构迁移说明
│   ├── COMPLETION_CHECKLIST.md # 完成清单
│   └── requirements.txt        # Python 依赖列表
│
├── 🚀 启动脚本
│   ├── run_app.command        # macOS 启动脚本（双击即可）
│   ├── run_app.bat            # Windows 启动脚本（双击即可）
│   └── run_app.py             # 通用 Python 启动脚本
│
├── 📁 数据与备份
│   ├── data/                  # 数据备份（预留）
│   └── backups/               # 备份文件（预留）
│
└── .venv/                      # Python 虚拟环境（首次运行时创建）
```

## 🔧 配置说明

### 交易币种和汇率

所有交易记录时可指定：

| 字段 | 说明 | 示例 |
|------|------|------|
| **currency** | 交易币种代码 | JPY, USD, EUR, CNY 等 |
| **fx_to_jpy** | 币种对 JPY 的汇率换算 | USD 填 150 表示 1 USD = 150 JPY；JPY 填 1 |

所有成本和损益计算均以 **JPY 为基准** 转换。

### yfinance 自动拉取价格（可选）

yfinance 已在 `requirements.txt` 中，安装后可在"💰 价格/汇率"页面自动拉取最新价格。

⚠️ **注意**：
- 日本股票代码需要加 `.T` 后缀（例：7203.T 表示丰田）
- 港股加 `.HK` 后缀（例：0700.HK 表示腾讯）
- 需要网络连接；若网络问题可改用手动输入

## 📊 核心算法

### 移动平均成本法（Moving Average Cost Method）

持仓成本计算采用 **移动平均成本法**，记录每笔交易的时间顺序：

**BUY 交易**：
```
交易成本(JPY) = (数量 × 价格 + 手续费) × fx_to_jpy
新持仓 = 原持仓 + 买入数量
新成本基数 = 原成本基数 + 交易成本(JPY)
新均成本 = 新成本基数 / 新持仓
```

**SELL 交易**：
```
当前均成本 = 成本基数 / 持仓
卖出收入(JPY) = (数量 × 价格 - 手续费) × fx_to_jpy
本次成本 = 当前均成本 × 卖出数量
已实现P&L = 卖出收入 - 本次成本

新持仓 = 原持仓 - 卖出数量
新成本基数 = 原成本基数 - 本次成本
```

**Mark-to-Market（浮动盈亏）**：
```
未实现P&L = 当前市值 - 成本基数
当前市值 = 最新价格 × 持仓数量 × fx_to_jpy
```

所有金额在 **交易时即转换为 JPY** 基准，确保多币种环境下的准确计算。

## ❓ 常见问题

| 问题 | 答案 |
|------|------|
| **应用无法启动？** | 检查是否已运行启动脚本或 `streamlit run stocktool/app.py`；确保 Python ≥ 3.10 |
| **导入 CSV 失败？** | 检查 CSV 列名映射是否正确；是否有必需列（date, ticker, side, qty, price, currency） |
| **浮动盈亏显示 NaN？** | 需要先在"💰 价格/汇率"页面录入或拉取最新价格 |
| **支持多账户吗？** | 当前版本不区分账户，所有交易混合计算。后续可添加 account 字段实现多账户 |
| **支持期权/期货吗？** | 当前支持现货交易。可扩展 schema 添加到期日、行权价等字段 |
| **如何导出数据？** | 可在"📃 交易列表"页复制表格，或用 SQLite 工具直接查询 portfolio.db 文件 |
| **可以在线部署吗？** | 可以。迁移数据库到云 SQLite（如 Supabase）即可部署到 Streamlit Cloud |
| **支持 iOS/Android？** | 浏览器打开 http://localhost:8501 即可使用；不支持原生应用 |

## 🛠️ 技术栈

| 组件 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.10+ | 编程语言 |
| **Streamlit** | ≥1.28.0 | Web UI 框架 |
| **pandas** | ≥2.2.0 | 数据处理与分析 |
| **numpy** | ≥1.24.0 | 数值计算 |
| **yfinance** | ≥0.2.30 | 股票价格数据（可选） |
| **SQLite** | 内置 | 本地数据库 |

## 🚦 开发与扩展

### 参考文档

- **[FEATURES.md](FEATURES.md)** - 完整功能清单及版本历史
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - AI 开发指南（架构、模式、常见任务）
- **[QUICK_START.md](QUICK_START.md)** - 用户快速入门
- **[MIGRATION.md](MIGRATION.md)** - 从 CLI 迁移到 Streamlit 的细节

### 添加新功能

参考 [.github/copilot-instructions.md](.github/copilot-instructions.md) 了解：
- ✅ 添加新的交易字段
- ✅ 扩展 Dashboard 指标
- ✅ 修改 P&L 计算逻辑
- ✅ 新增 CSV 导入格式

所有改进都会记录在 [FEATURES.md](FEATURES.md) 的"版本更新历史"中。

### 运行测试

```bash
pytest tests/
```

## 📋 更新日志

**v1.0.0 - 2026-01-28**
- ✅ 完整的 Streamlit Web UI（6 个页面）
- ✅ SQLite 本地数据库
- ✅ 移动平均成本法位置计算
- ✅ 多币种支持和自动转换
- ✅ CSV 批量导入
- ✅ yfinance 自动价格拉取
- ✅ 跨平台启动脚本（macOS, Windows, 通用）
- ✅ 完整文档和开发指南

详见 [FEATURES.md](FEATURES.md)

---

## 📄 许可证与声明

本项目为个人投资追踪工具。

⚠️ **免责声明**：
- 本工具不提供任何投资建议
- 所有计算结果仅供参考
- 使用者对自己的投资决策全权负责
- 作者不承担因使用本工具而产生的任何损失

---

## 📧 反馈与贡献

如有问题或建议，欢迎提交 Issue 或 Pull Request。

**致谢**：感谢 Streamlit、pandas、yfinance 等开源项目的支持。

---

**⭐️ 如果这个工具对你有帮助，请给个 Star！**

*最后更新：2026-01-28*
