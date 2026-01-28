# 📒 Stock Journal 功能清单

**最后更新**: 2026-01-28  
**应用版本**: 1.0.0  
**开发状态**: ✅ 完全就绪

---

## 📋 目录

1. [核心功能模块](#核心功能模块)
2. [页面功能详表](#页面功能详表)
3. [业务逻辑功能](#业务逻辑功能)
4. [数据管理功能](#数据管理功能)
5. [计算引擎](#计算引擎)
6. [辅助功能](#辅助功能)
7. [版本更新历史](#版本更新历史)

---

## 核心功能模块

### 🎯 应用级功能

| 功能 | 描述 | 状态 |
|------|------|------|
| **Web UI 界面** | 使用 Streamlit 构建的响应式Web界面 | ✅ |
| **侧边栏导航** | 6个主要功能页面的单选导航 | ✅ |
| **数据库初始化** | 首次启动自动创建 SQLite 数据库和表结构 | ✅ |
| **多币种支持** | JPY、USD 等多币种交易记录和换算 | ✅ |
| **基准币种（JPY）** | 所有 P&L 计算统一使用 JPY 作为基准 | ✅ |

---

## 页面功能详表

### 1️⃣ **➕ 录入交易** - 添加单笔交易记录

**功能**：手动输入一笔投资交易（买入或卖出）

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| 日期 | 日期 | ✅ | 今天 | 交易执行日期 |
| Ticker | 文本 | ✅ | - | 股票代码（如 AAPL, 7203.T） |
| 方向 | 下拉 | ✅ | - | BUY（买入）或 SELL（卖出） |
| 数量 | 数字 | ✅ | 1.0 | 交易股数（必须 > 0） |
| 成交价 | 数字 | ✅ | 0.0 | 以交易币种表示的价格 |
| 币种 | 文本 | ✅ | JPY | 交易币种代码（JPY/USD/CNY等） |
| 手续费 | 数字 | ✅ | 0.0 | 以交易币种表示的交易费用 |
| fx_to_jpy | 数字 | ✅ | 1.0 | 汇率换算因子（1币种 = ?JPY） |
| 备注 | 文本 | ❌ | - | 可选备注信息 |

**操作**：
- 💾 点击"保存"按钮提交交易
- ✅ 成功提示确认交易已保存
- ❌ 错误提示（Ticker 为空、数量≤0等）

**数据验证**：
- Ticker 必填且自动转换为大写
- 数量必须 > 0
- 交易币种自动转换为大写
- 所有数值自动转换为浮点数

---

### 2️⃣ **📥 导入 CSV** - 批量导入交易记录

**功能**：从券商导出的 CSV 文件批量导入交易数据

**工作流程**：
1. 📤 上传 CSV 文件
2. 👀 预览前 20 行数据
3. 🔄 配置列名映射
4. 📥 一键导入到数据库

**列映射配置**：

| 目标字段 | 是否必需 | 备注 |
|---------|---------|------|
| trade_date | ✅ 必需 | 自动转换为 YYYY-MM-DD 格式 |
| ticker | ✅ 必需 | 自动转换为大写 |
| side | ✅ 必需 | 自动转换为大写；B→BUY，S→SELL |
| quantity | ✅ 必需 | 自动转换为浮点数 |
| price | ✅ 必需 | 自动转换为浮点数 |
| currency | ✅ 必需 | 自动转换为大写 |
| fees | ❌ 可选 | 默认 0.0；若不选填充为 0.0 |
| fx_to_jpy | ❌ 可选 | 默认 1.0；若不选填充为 1.0 |
| note | ❌ 可选 | 保存为文本或 NULL |

**特性**：
- 灵活的列映射（自动检测 CSV 列并让用户选择对应字段）
- 批量插入优化
- 显示导入结果数量
- 异常处理和错误提示

---

### 3️⃣ **📃 交易列表** - 查看所有交易记录

**功能**：显示历史交易明细表

**显示列**：
- id (交易ID)
- trade_date (交易日期)
- ticker (股票代码)
- side (交易方向：BUY/SELL)
- quantity (数量)
- price (成交价)
- currency (币种)
- fees (手续费)
- fx_to_jpy (汇率)
- note (备注)

**交互功能**：
- 🔍 **Ticker 筛选**：按股票代码过滤显示
- 📊 **显示限制**：设置显示行数（默认100行）
- 📋 **数据排序**：按 trade_date 和 id 正序显示（最旧→最新）
- 💾 **表格导出**：Streamlit 原生支持复制到剪贴板

**特点**：
- 自动按时间顺序排序（chronological order）
- 留空 Ticker 筛选则显示全部
- 如果记录为空显示警告提示

---

### 4️⃣ **📦 持仓汇总** - 当前投资组合概览

**功能**：计算当前持仓状态和 P&L（使用移动平均成本法）

**显示列**（JPY 口径）：

| 列名 | 含义 | 计算方式 |
|-----|------|--------|
| ticker | 股票代码 | - |
| 数量 | 当前持有股数 | BUY累加 - SELL累减 |
| 均成本(JPY) | 单位平均成本 | 成本基数 / 数量 |
| 成本(JPY) | 总成本基数 | 按历史成本累计 |
| 市值(JPY) | 当前市值 | 最新价格 × 数量 × 汇率 |
| 已实现(JPY) | 已实现损益 | 历史卖出的 P&L 累计 |
| 未实现(JPY) | 未实现损益 | 市值 - 成本基数 |

**特性**：
- ✅ 使用**移动平均成本法**准确计算持仓成本
- ✅ **多币种自动转换**为 JPY
- ✅ **mark-to-market 市值计算**（需要先在"价格/汇率"页录入最新价格）
- ✅ 按市值从大到小排序
- ⚠️ 检测负持仓（做空）并显示警告

**数据验证**：
- 无交易时显示警告提示
- 若某 ticker 未录入价格，市值显示 NaN，未实现损益也为 NaN
- 负持仓（先卖后买）会显示警告提示用户检查

---

### 5️⃣ **📊 Dashboard** - 投资组合概览和 KPI

**功能**：展示关键投资指标和收益分析

**KPI 卡片**：

| 指标 | 单位 | 说明 |
|-----|------|------|
| 持仓成本（JPY） | JPY | 当前所有持仓的总成本基数 |
| 已实现损益（JPY） | JPY | 历史卖出单据产生的盈损总和 |
| 未实现损益（JPY） | JPY | 当前持仓市值与成本的差额（需有价格数据） |
| 总收益率 % | % | (已实现 + 未实现) / 成本基数 × 100% |

**收益分析**：
- 📊 **按 Ticker 的已实现损益**：表格显示每个 ticker 的盈损情况
- 📉 数据按已实现损益从大到小排序
- 💡 总收益率动态计算（需要有市价数据）

**特点**：
- 实时汇总所有投资位置
- 区分已实现和未实现 P&L
- 收益率百分比计算
- 若没有价格数据则显示"—（先录入价格）"

---

### 6️⃣ **💰 价格/汇率** - 市场数据维护

**功能**：管理股票最新价格和汇率，用于 mark-to-market 计算

#### 📝 模式 1：手动输入

**输入字段**：
- Ticker：股票代码
- 日期（asof）：价格有效日期
- 最新价格：以交易币种表示
- 币种：JPY/USD/CNY等
- fx_to_jpy：汇率（1币种 = ?JPY）

**操作**：点击"💾 保存价格"按钮

#### 🔄 模式 2：自动拉取（yfinance）

**特性**：
- ✅ 自动检测 yfinance 是否可用
- ✅ 支持国际股票（如 AAPL）和日本股票（如 7203.T）
- ✅ 自动获取当前价格和币种信息
- ✅ 自动填充汇率字段
- ✅ Best-effort 设计（失败优雅降级）
- ❌ 网络问题、ticker 格式错误等均提示用户改用手动输入

**yfinance 局限**：
- 需要网络连接
- 某些股票可能无法拉取
- 日本股票需要特殊格式（如 7203.T）
- 开盘前可能无法获取最新价格

#### 📋 价格记录列表

**显示所有已维护的价格**：
- ticker
- price（最新价格）
- currency（币种）
- fx_to_jpy（汇率）
- asof（数据日期）

**特点**：
- INSERT ON CONFLICT 冲突解决（同一 ticker 自动更新）
- 按 ticker 唯一性维护

---

## 业务逻辑功能

### 📐 位置计算引擎 - `compute_positions()`

**算法**：**移动平均成本法（Moving Average Cost Method）**

#### 工作原理

1. **BUY 交易**：
   ```
   交易成本(JPY) = (数量 × 成交价 + 手续费) × 汇率
   新持仓数量 = 原持仓 + 买入数量
   新成本基数 = 原成本 + 交易成本(JPY)
   新平均成本 = 新成本基数 / 新持仓数量
   ```

2. **SELL 交易**：
   ```
   当前平均成本 = 成本基数 / 持仓数量
   卖出收入(JPY) = (数量 × 成交价 - 手续费) × 汇率
   本次成本 = 平均成本 × 卖出数量
   本次P&L = 卖出收入 - 本次成本
   已实现P&L += 本次P&L
   
   新持仓数量 = 原持仓 - 卖出数量
   新成本基数 = 原成本 - 本次成本
   ```

3. **最终状态**：
   ```
   平均成本 = 最终成本基数 / 最终持仓数量（若数量>0）
   ```

#### 特性

- ✅ **按 ticker 分组处理**
- ✅ **按时间顺序（trade_date, id）处理**
- ✅ **支持负持仓**（short sale 场景）
- ✅ **多币种自动转换为 JPY**
- ✅ **精确追踪已实现 P&L**
- ✅ **处理交易手续费**

#### 返回数据

DataFrame，每行代表一个 ticker：
```
ticker, quantity, avg_cost_jpy, cost_basis_jpy, realized_pnl_jpy
```

---

### 💱 多币种转换 - `jpy_value()`

**功能**：将任意币种的价格转换为 JPY

**公式**：
```
JPY值 = 价格 × 数量 × 汇率(fx_to_jpy)
```

**示例**：
- USD 价格 100，数量 10，汇率 150 → JPY 值 = 100 × 10 × 150 = 150,000 JPY
- JPY 价格 1000，数量 100，汇率 1 → JPY 值 = 1000 × 100 × 1 = 100,000 JPY

**应用场景**：
- 计算交易成本
- 计算卖出收入
- 计算市值
- Dashboard 中的总和计算

---

### 📊 市场数据获取 - `try_fetch_price_yf()`

**功能**：尝试从 yfinance 自动获取股票最新价格

**输入**：
- ticker：股票代码（字符串）

**输出**：
- 成功：`(price, currency)` 元组
- 失败：`None`

**特点**：
- ✅ Best-effort 设计（失败不抛异常）
- ✅ 自动检测 yfinance 是否可用
- ✅ 支持 fast_info API（快速获取）
- ✅ 降级到历史数据（5日K线）
- ✅ 异常捕获和日志（错误直接返回None）

**支持的 ticker 格式**：
- 美国股票：AAPL, MSFT, GOOG
- 日本股票：7203.T（Toyota）, 9984.T（SoftBank）
- 港股：0700.HK（Tencent）
- 其他国际交易所票

---

## 数据管理功能

### 🗄️ 数据库管理 - `db.py`

#### 连接管理 - `get_conn()`

**功能**：创建 SQLite 数据库连接

**特点**：
- ✅ 自动启用外键约束（PRAGMA foreign_keys = ON）
- ✅ 返回原生 sqlite3 Connection 对象
- ✅ 支持手动关闭和上下文管理

**使用模式**：
```python
conn = get_conn()
# ... 执行 SQL 操作 ...
conn.commit()
conn.close()
```

#### 数据库初始化 - `init_db()`

**功能**：创建表结构和索引（幂等操作）

**表结构**：

##### trades 表
```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date TEXT NOT NULL,        -- YYYY-MM-DD 格式
    ticker TEXT NOT NULL,            -- 股票代码（大写）
    side TEXT NOT NULL,              -- 'BUY' 或 'SELL'
    quantity REAL NOT NULL,          -- 交易数量
    price REAL NOT NULL,             -- 成交价（交易币种）
    currency TEXT NOT NULL,          -- 币种代码（大写）
    fees REAL NOT NULL DEFAULT 0,    -- 手续费（交易币种）
    fx_to_jpy REAL NOT NULL DEFAULT 1.0,  -- 汇率因子
    note TEXT,                       -- 备注信息
    CHECK(side IN ('BUY', 'SELL')),  -- 方向约束
    CHECK(quantity > 0),             -- 数量约束
    CHECK(price >= 0)                -- 价格约束
);

-- 索引以加速查询
CREATE INDEX idx_trades_ticker ON trades(ticker);
CREATE INDEX idx_trades_date ON trades(trade_date);
```

##### prices 表
```sql
CREATE TABLE prices (
    ticker TEXT PRIMARY KEY,         -- 股票代码（唯一）
    price REAL NOT NULL,             -- 最新价格
    currency TEXT NOT NULL,          -- 币种
    fx_to_jpy REAL NOT NULL,         -- 汇率
    asof TEXT NOT NULL               -- 数据日期
);
```

#### 价格更新 - `upsert_price()`

**功能**：更新或插入价格记录

**实现**：
```sql
INSERT INTO prices (ticker, price, currency, fx_to_jpy, asof)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(ticker) DO UPDATE SET
    price = excluded.price,
    fx_to_jpy = excluded.fx_to_jpy,
    asof = excluded.asof
```

**特点**：
- ✅ 自动覆盖同 ticker 的旧数据
- ✅ 原子操作（事务安全）
- ✅ 高性能

---

### 📖 数据查询功能

#### 交易查询 - `read_trades()`

**功能**：从数据库读取所有交易

**排序**：trade_date (ASC) → id (ASC)

**转换**：trade_date 自动转为 pandas datetime 类型

**返回**：
```
DataFrame [id, trade_date, ticker, side, quantity, price, currency, fees, fx_to_jpy, note]
```

#### 价格查询 - `read_prices()`

**功能**：从数据库读取所有价格记录

**返回**：
```
DataFrame [ticker, price, currency, fx_to_jpy, asof]
```

---

## 计算引擎

### 🔄 P&L 计算链路

```
导入/录入交易
    ⬇️
read_trades() 从数据库读取
    ⬇️
compute_positions() 计算当前持仓
    ├─ 按 ticker 分组
    ├─ 按时间顺序处理每笔交易
    ├─ 计算每个 ticker 的数量、平均成本、成本基数、已实现P&L
    └─ 返回持仓DataFrame
    
    ⬇️
read_prices() 读取最新价格
    ⬇️
jpy_value() 计算市值（JPY）
    ⬇️
未实现P&L = 市值 - 成本基数
    
    ⬇️
总收益率 = (已实现 + 未实现) / 成本 × 100%
```

### 📊 Dashboard 聚合逻辑

```
按 ticker 聚合
    ⬇️
求和：
  - 总成本 = Σ(cost_basis_jpy)
  - 总市值 = Σ(price × qty × fx) 对所有持仓
  - 总已实现 = Σ(realized_pnl_jpy)
    ⬇️
计算：
  - 总未实现 = 总市值 - 总成本
  - 总收益率 = (总已实现 + 总未实现) / 总成本 × 100%
```

---

## 辅助功能

### ✅ 数据验证

#### 录入交易页面

| 验证项 | 规则 | 错误提示 |
|-------|------|--------|
| Ticker | 不能为空 | ❌ Ticker 不能为空 |
| 数量 | 必须 > 0 | ❌ 数量必须 > 0 |
| 自动大写 | ticker, side, currency | 自动转换 |

#### CSV 导入

| 验证项 | 规则 | 处理 |
|-------|------|------|
| 必需列 | trade_date, ticker, side, qty, price, currency | 用户选择映射 |
| 可选列 | fees, fx_to_jpy, note | 默认值填充 |
| 日期转换 | str → datetime → YYYY-MM-DD | 自动转换 |
| 方向映射 | B/SELL → BUY; S/sell → SELL | 自动规范化 |

#### 持仓计算

| 验证项 | 规则 | 提示 |
|-------|------|------|
| 交易排序 | chronological (date, id) | 自动排序 |
| 负持仓 | qty < 0 检测 | ⚠️ 显示警告 |
| 缺失价格 | NaN 处理 | 显示 NaN；未实现损益为 NaN |

### 📢 UI 反馈提示

| 提示类型 | 用途 | 示例 |
|---------|------|------|
| ✅ success | 操作成功 | "✅ 已保存：..." |
| ❌ error | 操作失败 | "❌ Ticker 不能为空" |
| ⚠️ warning | 数据异常 | "⚠️ 检测到负持仓..." |
| ℹ️ info | 信息提示 | "ℹ️ 暂无价格记录" |

### 🎨 UI 组件

| 组件 | 功能 |
|-----|------|
| st.form() | 保留状态的表单输入 |
| st.columns() | 多列布局 |
| st.dataframe() | 可交互的表格显示 |
| st.number_input() | 数值输入 |
| st.text_input() | 文本输入 |
| st.selectbox() | 下拉菜单 |
| st.date_input() | 日期选择 |
| st.file_uploader() | 文件上传 |
| st.metric() | KPI 指标卡 |
| st.divider() | 分隔线 |
| st.spinner() | 加载提示 |

---

## 版本更新历史

### v1.0.0 - 2026-01-28 ✅ 初版发布

**新增功能**：
- ➕ 录入交易 - 单笔交易手动输入
- 📥 导入CSV - 批量导入交易
- 📃 交易列表 - 查看历史交易
- 📦 持仓汇总 - 计算当前持仓（移动平均成本法）
- 📊 Dashboard - 投资组合概览和 KPI
- 💰 价格/汇率 - 市场数据维护（手动/自动）

**核心引擎**：
- 移动平均成本法位置计算
- 多币种自动转换为 JPY
- Mark-to-market 未实现 P&L
- 已实现 P&L 精确追踪

**数据层**：
- SQLite 本地数据库
- 两表模型（trades, prices）
- 外键约束和数据验证
- 原子事务操作

**用户体验**：
- 完整的数据验证
- 友好的错误提示
- 多平台启动脚本
- 详细的文档说明

**技术栈**：
- Python 3.12.4
- Streamlit ≥ 1.28.0
- pandas ≥ 2.2.0
- numpy ≥ 1.24.0
- yfinance ≥ 0.2.30 (可选)
- sqlite3 (内置)

---

## 📝 功能维护说明

### 如何添加新功能

1. **在本文件中新增功能描述**
   - 在对应功能分类中补充详情
   - 更新目录
   - 标注实现状态

2. **更新代码后同步文档**
   - 修改 `stocktool/app.py` 或 `stocktool/db.py`
   - 在本文件相应部分更新说明
   - 在"版本更新历史"中新增版本记录

3. **版本记录格式**
   ```markdown
   ### vX.Y.Z - YYYY-MM-DD

   **新增功能**：
   - 功能 1
   - 功能 2

   **改进**：
   - 改进 1

   **修复**：
   - 修复 1
   ```

### 功能开发 checklist

- [ ] 在 `app.py` 实现功能代码
- [ ] 在 `db.py` 中添加必要的数据库操作
- [ ] 添加输入验证和错误处理
- [ ] 测试功能的各个场景
- [ ] 更新本文档
- [ ] 更新 `README.md`（如需用户重点关注）
- [ ] 提交 commit 并标注版本号

---

## 📊 功能矩阵

| 功能页面 | 数据输入 | 数据输出 | 依赖功能 | 优先级 |
|---------|---------|---------|---------|-------|
| 录入交易 | 表单 | trades表 | 数据库 | 🔴 高 |
| 导入CSV | 文件 | trades表 | 数据库、数据清理 | 🔴 高 |
| 交易列表 | 数据库 | 表格 | 数据库查询 | 🟡 中 |
| 持仓汇总 | trades + prices | 持仓表 | 位置计算、多币种 | 🔴 高 |
| Dashboard | trades + prices | KPI卡片、图表 | 位置计算、聚合 | 🟡 中 |
| 价格/汇率 | 表单/API | prices表 | 数据库、yfinance | 🟡 中 |

---

**📝 本文档会随应用改进不断完善。最后更新于 2026-01-28。**
