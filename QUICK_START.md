# StockAnalysis - Quick Start Guide

## 🚀 安装和运行

### 第一次使用

```bash
# 1. 克隆项目（如未克隆）
git clone https://github.com/Teikn/StockAnalysis.git
cd StockAnalysis

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
streamlit run stocktool/app.py
```

应用会自动在浏览器打开：http://localhost:8501

### 后续使用

```bash
# 激活虚拟环境
source .venv/bin/activate

# 启动应用
streamlit run stocktool/app.py
```

---

## 📖 功能导航

### 1. ➕ 录入交易
- 手动输入单笔交易
- 支持的币种：JPY, USD, EUR 等
- 费用自动计入成本

### 2. 📥 导入CSV
- 上传券商导出的交易记录
- 灵活选择列映射
- 支持批量导入

### 3. 📃 交易列表
- 查看全部历史交易
- 按 Ticker 筛选
- 按时间倒序排列

### 4. 📦 持仓汇总
- 当前持仓数量
- 均成本（JPY）
- 成本基础
- 已实现损益
- 未实现损益（需要先输入价格）

### 5. 📊 Dashboard
- 持仓成本总计
- 已实现损益
- 未实现损益
- 总收益率
- Ticker 盈亏分布

### 6. 💰 价格/汇率
- 手动输入最新价格
- 自动拉取（yfinance）
- 支持日本股票（需要 .T 后缀）

---

## 💾 数据管理

**数据库位置：** `stocktool/portfolio.db`

### 重置数据库

```bash
# 方法1：直接删除文件
rm stocktool/portfolio.db

# 方法2：重新启动应用（会自动重建空数据库）
streamlit run stocktool/app.py
```

### 备份数据

```bash
# 备份数据库文件
cp stocktool/portfolio.db backups/portfolio_backup_$(date +%Y%m%d_%H%M%S).db
```

### 导出数据

使用 SQLite 命令行工具：
```bash
sqlite3 stocktool/portfolio.db "SELECT * FROM trades;" > trades_export.csv
```

---

## 🔍 常见操作

### 添加美股交易（USD）

1. 进入 **➕ 录入交易**
2. 填写信息：
   - Ticker: `AAPL`
   - 币种: `USD`
   - fx_to_jpy: `150`（当前 USD->JPY 汇率）
   - 其他字段正常填写

### 添加日本股票交易

1. 进入 **➕ 录入交易**
2. 填写信息：
   - Ticker: `7203.T`（丰田）
   - 币种: `JPY`
   - fx_to_jpy: `1`
   - 其他字段正常填写

### 自动拉取股票价格

1. 进入 **💰 价格/汇率**
2. 选择 **尝试自动拉取(yfinance)**
3. 输入 Ticker（例：AAPL 或 7203.T）
4. 输入 fx_to_jpy
5. 点击 **自动拉取并保存**

### 计算浮动盈亏

浮动盈亏 = 当前市值 - 成本基础

需要：
1. ✅ 已录入交易
2. ✅ 已输入该 Ticker 的最新价格

---

## ⚙️ 配置和优化

### Streamlit 快捷键

- `R` 重新运行应用
- `C` 清除缓存
- `P` 打开参数设置

### 性能优化

如果应用变慢：
1. 检查交易记录数量（超过 10000 条可能较慢）
2. 考虑归档旧交易到备份文件
3. 清除浏览器缓存

---

## 🐛 故障排除

| 问题 | 解决方案 |
|------|--------|
| 浮动盈亏显示 NaN | 在"💰 价格/汇率"页输入价格 |
| yfinance 拉取失败 | 检查网络连接或 Ticker 格式 |
| 数据库连接错误 | 删除 `portfolio.db` 重启应用 |
| 应用启动缓慢 | 清除 `.streamlit/` 下的缓存文件 |
| 负持仓显示警告 | 检查交易数据，确认是否有误 |

---

## 📚 更多信息

- **AI 开发指南：** `.github/copilot-instructions.md`
- **迁移说明：** `MIGRATION.md`
- **项目文档：** `README.md`

---

## 💡 Tips

- 💡 所有交易自动以 JPY 为基准转换成本
- 💡 支持负持仓（做空），但 UI 会给出警告
- 💡 CSV 导入时，列名映射会记住上次选择
- 💡 定期备份 `portfolio.db` 避免数据丢失
- 💡 日本股票代码需要 `.T` 后缀（例：6758.T = Sony）
