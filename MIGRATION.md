# Migration Guide: Typer CLI → Streamlit Web UI

## Overview

StockAnalysis has migrated from a **Typer-based CLI tool** to a **Streamlit-based Web UI**.
This document explains the changes and how the new architecture works.

## 🔄 Architecture Changes

### Before (Typer CLI)
```
stocktool/
├── cli.py           # Typer command interface
├── models.py        # SQLModel ORM definitions
├── db.py            # SQLAlchemy engine management
├── services/
│   ├── trades.py    # CRUD operations
│   └── portfolio.py # Position calculation
```

**Usage:**
```bash
python -m stocktool add AAPL buy 10 175.3 --fee 1.2
python -m stocktool list
python -m stocktool positions
```

### After (Streamlit UI)
```
stocktool/
├── app.py           # Streamlit multi-page UI + business logic
├── db.py            # Raw sqlite3 connection management
├── portfolio.db     # SQLite database file
├── cli.py           # DEPRECATED (kept for reference)
├── models.py        # DEPRECATED (kept for reference)
└── services/        # DEPRECATED (kept for reference)
```

**Usage:**
```bash
streamlit run stocktool/app.py
# Opens http://localhost:8501 in browser
```

## 📊 Key Technical Changes

| Aspect | Before | After |
|--------|--------|-------|
| **Framework** | Typer CLI | Streamlit Web UI |
| **Database** | SQLAlchemy + SQLModel ORM | Raw sqlite3 |
| **Architecture** | Layered (CLI → Services → Models → DB) | Monolithic (app.py contains UI + logic) |
| **Database Path** | `data/stocktool.db` | `stocktool/portfolio.db` |
| **Session Management** | `session_scope(engine)` context manager | `get_conn()` raw connections |
| **Type Hints** | SQLModel with Pydantic | pandas DataFrames + basic Python types |
| **Data Queries** | SQLModel `select()` API | Raw SQL strings with `pd.read_sql_query()` |

## 🗄️ Database Schema (Unchanged)

The database schema remains **identical**:

**trades table:**
```sql
id, trade_date, ticker, side, quantity, price, 
currency, fees, fx_to_jpy, note
```

**prices table:**
```sql
ticker (PK), price, currency, fx_to_jpy, asof
```

### Data Migration

If you had an old `data/stocktool.db` (Typer version):
1. **Option A (Keep Data):** Copy to new location:
   ```bash
   cp data/stocktool.db stocktool/portfolio.db
   ```
2. **Option B (Fresh Start):** Delete old database; Streamlit will auto-init

## 📝 Code Structure

### Business Logic: Position Computation
Moved from `services/portfolio.py` → `app.py` as `compute_positions()`

**Algorithm unchanged** - still uses moving average cost method:
```python
def compute_positions(trades: pd.DataFrame) -> pd.DataFrame:
    # BUY: weighted average cost
    # SELL: realize P&L at avg cost
    # Returns: ticker, quantity, avg_cost_jpy, cost_basis_jpy, realized_pnl_jpy
```

### UI: Page Management
Instead of separate Typer commands, now uses Streamlit page radio:

```python
page = st.sidebar.radio("功能", [
    "➕ 录入交易",      # Add Trade (replaces: python -m stocktool add ...)
    "📥 导入CSV",       # Import CSV
    "📃 交易列表",      # List (replaces: python -m stocktool list)
    "📦 持仓汇总",      # Positions (replaces: python -m stocktool positions)
    "📊 Dashboard",     # NEW
    "💰 价格/汇率"      # NEW
])
```

## 🔗 Dependencies

### Removed
- `typer[all]` - CLI framework (no longer needed)
- `sqlmodel` - ORM (replaced with raw sqlite3)
- `SQLAlchemy` - ORM engine (replaced with raw sqlite3)
- `tabulate` - CLI table formatting (Streamlit handles UI)

### Added
- `streamlit` - Web UI framework
- `yfinance` - Optional price fetching

### Updated
- `requirements.txt` - See file for current versions

## 🚀 Development Workflow

### Running the Application

**Old way (Typer):**
```bash
python -m stocktool init
python -m stocktool add AAPL buy 10 175.3
python -m stocktool list
```

**New way (Streamlit):**
```bash
# One command starts the server
streamlit run stocktool/app.py

# Use browser UI instead of CLI commands
```

### Adding Features

**Old pattern:**
1. Add command in `cli.py` with `@app.command()`
2. Implement logic in `services/`
3. Use `session_scope()` for DB access

**New pattern:**
1. Add UI section in `app.py` within page conditional
2. Implement logic directly in `app.py`
3. Use `get_conn()` for DB access
4. Use Streamlit widgets (`st.form()`, `st.dataframe()`, etc.)

## ⚠️ Backwards Compatibility

The old files (`cli.py`, `models.py`, `services/`) are **kept but deprecated**:
- They are no longer used by the main application
- They may be removed in future versions
- Kept as reference for understanding the old architecture

## 🔄 Migration Checklist

- [x] Replace SQLAlchemy/SQLModel with raw sqlite3
- [x] Create Streamlit multi-page app (`app.py`)
- [x] Port `compute_positions()` logic to new architecture
- [x] Update database path: `data/stocktool.db` → `stocktool/portfolio.db`
- [x] Update requirements.txt
- [x] Update README.md with Streamlit instructions
- [x] Update .github/copilot-instructions.md
- [x] Create .streamlit/config.toml for UI customization
- [ ] (Optional) Add more Dashboard visualizations
- [ ] (Optional) Add support for additional assets (crypto, commodities)

## 📚 Further Reading

- Streamlit Docs: https://docs.streamlit.io/
- SQLite Docs: https://www.sqlite.org/cli.html
- Project AI Instructions: `.github/copilot-instructions.md`

## 🤝 Contributing

When adding features:
1. Always use `get_conn()` for database access
2. Convert DB results to pandas DataFrames for analysis
3. Use Streamlit components for UI (forms, tables, metrics)
4. Keep `app.py` structured by page (one conditional block per page)
5. Document in `.github/copilot-instructions.md` if pattern is new
