# AI Coding Agent Instructions for StockAnalysis

## Project Overview
Local Python investment tracking tool combining **Streamlit UI + SQLite DB + pandas analysis**.
For personal stock/fund trading records, position tracking, P&L calculation (realized & unrealized).

**Stack:** Python 3.x | Streamlit | sqlite3 | pandas | yfinance (optional)

---

## Architecture & Data Flow

### Core Components
1. **UI Layer** (`stocktool/app.py`): Single-file Streamlit multi-page app (pages via sidebar radio)
2. **Data Layer** (`stocktool/db.py`): Raw sqlite3 + connection pooling with PRAGMA foreign_keys
3. **Business Logic** (in `app.py`):
   - `read_trades()`, `read_prices()`: SQL→pandas queries
   - `compute_positions()`: Moving average cost calculation
   - `jpy_value()`: Currency conversion helper
   - `try_fetch_price_yf()`: Optional yfinance price fetching

### Data Model (SQLite Schema)

**trades table:**
```sql
id (INTEGER PK), trade_date (TEXT YYYY-MM-DD), ticker (TEXT),
side (TEXT: 'BUY'/'SELL'), quantity (REAL), price (REAL),
currency (TEXT), fees (REAL), fx_to_jpy (REAL), note (TEXT)
```
- Indexes: `ticker`, `trade_date` (for chronological queries)
- CHECK constraints: `side IN ('BUY','SELL')`, `quantity > 0`, `price >= 0`

**prices table:**
```sql
ticker (TEXT PK), price (REAL), currency (TEXT),
fx_to_jpy (REAL), asof (TEXT YYYY-MM-DD)
```
- Used for mark-to-market unrealized P&L calculation
- Upsert-on-conflict pattern for daily updates

### Critical Workflow: Position Computation

`compute_positions(trades_df)` implements **moving average cost method**:

**Per ticker, chronological walk (sorted by trade_date, id):**

1. **BUY:**
   ```
   cost_jpy = (qty × price + fees) × fx_to_jpy
   qty_new = qty_old + purchase_qty
   cost_basis_new = cost_basis_old + cost_jpy
   avg_cost = cost_basis_new / qty_new
   ```

2. **SELL:**
   ```
   avg_cost = cost_basis / qty  (before sale)
   proceeds_jpy = (qty × price - fees) × fx_to_jpy
   realized_pnl += (proceeds_jpy - avg_cost × qty)
   qty_new = qty_old - sale_qty
   cost_basis_new = cost_basis_old - (avg_cost × sale_qty)
   ```

3. **Result per ticker:**
   - `quantity`, `avg_cost_jpy`, `cost_basis_jpy`, `realized_pnl_jpy`
   - **All amounts in JPY base** (convert via `fx_to_jpy` at trade time)

---

## Database & Session Management

**Pattern:** Context-managed connections via `get_conn()`
```python
from db import get_conn

conn = get_conn()  # Auto-enables PRAGMA foreign_keys
conn.execute("INSERT INTO trades (...) VALUES (...)", (...))
conn.commit()
conn.close()
```

**Key Behaviors:**
- `init_db()` creates `portfolio.db` in project root (check `DB_PATH`)
- `get_conn()` enforces foreign key constraints (PRAGMA foreign_keys = ON)
- Always `conn.close()` after use (or use try/finally wrapper)
- Read-only queries skip `.commit()`
- Use `pd.read_sql_query()` for SELECT → DataFrame conversion

**Schema Notes:**
- `ticker` stored UPPERCASE (normalize on insert with `.upper()`)
- `side` enforced by CHECK constraint ('BUY' or 'SELL' only)
- `fx_to_jpy = 1.0` for JPY trades; `>1.0` for USD (e.g., 150 if 1 USD = 150 JPY)
- `prices.ticker` is PK → allows `INSERT ... ON CONFLICT(...) DO UPDATE` upsert pattern

---

## Streamlit UI Structure

### Pages (via sidebar radio selector)
1. **➕ 录入交易**: Form to insert single trade (date, ticker, side, qty, price, currency, fees, fx_to_jpy, note)
2. **📥 导入CSV**: Upload & column-mapping for external broker CSV files
3. **📃 交易列表**: Display all trades as sortable DataFrame
4. **📦 持仓汇总**: Grouped positions with qty, avg_cost, cost_basis, market_value, realized/unrealized P&L
5. **📊 Dashboard**: KPI cards (total cost, total realized, total unrealized) + per-ticker realized P&L breakdown
6. **💰 价格/汇率**: Manual price entry OR auto-fetch via yfinance for mark-to-market

### Common Streamlit Patterns in This Project
```python
# Page selection (in main app flow)
page = st.sidebar.radio("功能", ["➕ 录入交易", "📥 导入CSV", ...])
if page == "➕ 录入交易":
    # page content

# Forms (preserve state across submit)
with st.form("form_key"):
    var = st.text_input("Label", value="default")
    if st.form_submit_button("Save"):
        # handle DB insert

# Metrics dashboard
c1, c2, c3 = st.columns(3)
c1.metric("Label", f"{value:,.0f}")

# DataFrames
st.dataframe(df, use_container_width=True)

# Error/info messages
st.error("Message")
st.success("Message")
st.warning("Message")
```

---

## Coding Conventions

### Import Style
```python
# Stdlib
import datetime as dt
from pathlib import Path

# Third-party
import pandas as pd
import numpy as np
import streamlit as st

# Optional
try:
    import yfinance as yf
    YF_OK = True
except Exception:
    YF_OK = False

# Local
from db import get_conn, init_db
```

### Data Handling
- **Dates:** Store as `TEXT (YYYY-MM-DD)` in DB; convert to `datetime` in pandas when needed
  ```python
  df["trade_date"] = pd.to_datetime(df["trade_date"])
  ```
- **Floats:** Use `float()` cast explicitly; `np.nan` for missing values
- **Categorical:** `ticker` UPPERCASE, `side` in {'BUY','SELL'}, `currency` in {'JPY','USD',...}

### SQL Queries
```python
# Read
df = pd.read_sql_query("SELECT * FROM trades ORDER BY trade_date DESC", conn)

# Write
conn.execute("INSERT INTO trades (...) VALUES (...)", (val1, val2, ...))
conn.commit()

# Upsert
conn.execute("""
    INSERT INTO prices (ticker, price, currency, fx_to_jpy, asof)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(ticker) DO UPDATE SET price=excluded.price, fx_to_jpy=excluded.fx_to_jpy, asof=excluded.asof
""", (ticker, price, currency, fx, asof))
conn.commit()
```

---

## Common Tasks & Implementation Patterns

### Adding a New Trade Field
1. Alter schema in `db.py` `init_db()` → add column with default
   ```python
   cur.execute("""ALTER TABLE trades ADD COLUMN new_field TEXT DEFAULT NULL;""")
   ```
2. Update form in `app.py` `➕ 录入交易` → add `st.input_*()` widget
3. Update INSERT statement → include new column in VALUES tuple
4. If affects P&L: update `compute_positions()` loop

### Importing External CSV
1. User uploads file in `📥 导入CSV` page via `st.file_uploader()`
2. Read: `df = pd.read_csv(upload)`
3. Map columns: Each column selector via `st.selectbox()` (user picks which col → which field)
4. Normalize:
   ```python
   df["ticker"] = df[c_ticker].str.upper()
   df["side"] = df[c_side].str.upper().replace({"B":"BUY", "S":"SELL"})
   df["trade_date"] = pd.to_datetime(df[c_date]).dt.date.astype(str)
   ```
5. Batch insert:
   ```python
   conn.executemany("""INSERT INTO trades (...) VALUES (?, ?, ...)""",
                    list(df.itertuples(index=False, name=None)))
   conn.commit()
   ```

### Fetching Live Prices (Mark-to-Market)
- Function `try_fetch_price_yf(ticker)` returns `(price, currency)` tuple or `None`
- Wrapped in try/except; fallback if yfinance unavailable or network issue
- Stores in `prices` table via `upsert_price(ticker, price, currency, fx, asof)`
- In `📦 持仓汇总`, lookup price from `prices_map` dict:
  ```python
  prices_map = {r["ticker"]: r for _, r in prices.iterrows()}
  for _, pos in positions.iterrows():
      if pos["ticker"] in prices_map:
          p_info = prices_map[pos["ticker"]]
          market_value = p_info["price"] * pos["quantity"] * p_info["fx_to_jpy"]
          unrealized = market_value - pos["cost_basis_jpy"]
  ```

### Computing Unrealized P&L
```python
# In 📊 Dashboard or 📦 持仓汇总
total_cost = float(positions["cost_basis_jpy"].sum())
total_mkt = 0.0
for _, row in positions.iterrows():
    if ticker in prices_map:
        total_mkt += jpy_value(prices_map[ticker]["price"], row["quantity"], prices_map[ticker]["fx_to_jpy"])
total_unrealized = total_mkt - total_cost
```

---

## Integration Points & Dependencies

- **Streamlit**: Web framework; run via `streamlit run stocktool/app.py`
- **pandas**: DataFrames for aggregating trades; use `groupby().iterrows()` for position logic
- **yfinance** (optional): Auto-fetches stock prices; wrapped in try/except for robustness
- **sqlite3**: Built-in Python module; no extra setup needed
- **numpy**: For `np.nan` handling in unrealized P&L calculations

---

## Debugging Tips

- **Empty trades?** Check `portfolio.db` exists in project root; restart streamlit app after data insert
- **FX conversion wrong?** Verify `fx_to_jpy` values in trades table; trace `jpy_value(price, qty, fx)` calculation
- **Negative position?** Allowed (short), but UI shows warning; verify trade dates sorted correctly by `trade_date, id` in `compute_positions()`
- **Market value shows NaN?** Price not yet in `prices` table; user must manually enter or auto-fetch first
- **yfinance fails?** Check internet; ticker format (JP stocks need `.T` suffix, e.g., `7203.T`); fallback to manual input
- **CSV import hangs?** Large files (>10k rows) take seconds; check browser console for Streamlit logs
- **Negative quantities after sell?** Expected if short selling; check `side` values (must be 'BUY' or 'SELL')

---

## Development Workflow

**Run locally:**
```bash
cd /Users/tin/git/StockAnalysis
pip install streamlit pandas yfinance
streamlit run stocktool/app.py
# Opens http://localhost:8501 in browser
```

**Reset database:**
```bash
rm stocktool/portfolio.db
# Re-run streamlit; init_db() rebuilds schema automatically
```

**Add dependencies:**
```bash
pip install streamlit pandas yfinance
# Update requirements.txt after testing
```
