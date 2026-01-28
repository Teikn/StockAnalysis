"""
StockAnalysis Streamlit Application

A local investment tracking tool combining Streamlit UI + SQLite DB + pandas analysis.
Provides trading record management, portfolio position tracking, and P&L calculations
using a moving average cost method with JPY base currency.

Run: streamlit run stocktool/app.py
Opens: http://localhost:8501
"""

import datetime as dt
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

from db import DB_PATH, get_conn, init_db, upsert_price

# yfinance is optional - gracefully handle if not installed
try:
    import yfinance as yf
    YF_OK = True
except ImportError:
    YF_OK = False

# Constants
BASE_CCY = "JPY"  # All P&L calculations use JPY as base currency


# ============================================================================
# Database Helper Functions
# ============================================================================


def read_trades() -> pd.DataFrame:
    """
    Read all trades from database, sorted chronologically.
    
    Returns:
        pd.DataFrame: Trades with columns:
            id, trade_date, ticker, side, quantity, price, currency, fees, fx_to_jpy, note
            
    Note:
        trade_date is converted to datetime type in the returned DataFrame.
        Empty DataFrame if no trades exist.
    """
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM trades ORDER BY trade_date, id",
        conn
    )
    conn.close()
    
    if df.empty:
        return df
    
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


def read_prices() -> pd.DataFrame:
    """
    Read all price records from database.
    
    Returns:
        pd.DataFrame: Price records with columns:
            ticker, price, currency, fx_to_jpy, asof
            
    Note:
        Empty DataFrame if no prices exist.
    """
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM prices", conn)
    conn.close()
    return df


def jpy_value(price: float, qty: float, fx: float) -> float:
    """
    Convert price * quantity to JPY base amount.
    
    Formula: price × qty × fx_to_jpy
    
    Args:
        price: Price in trade currency
        qty: Quantity
        fx: Exchange rate (1 unit of currency = fx JPY)
        
    Returns:
        float: Amount in JPY
    """
    return float(price) * float(qty) * float(fx)


# ============================================================================
# Core Business Logic: Position Computation
# ============================================================================


def compute_positions(trades: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate portfolio positions using moving average cost method.
    
    Implements chronological walk-through of trades per ticker:
    - BUY: Increases position and cost basis (weighted average)
    - SELL: Realizes P&L and decrements position
    
    Args:
        trades: DataFrame with columns:
            trade_date, ticker, side, quantity, price, currency, fees, fx_to_jpy
            
    Returns:
        pd.DataFrame: Position summary with columns:
            ticker, quantity, avg_cost_jpy, cost_basis_jpy, realized_pnl_jpy
            
    Note:
        All amounts converted to JPY base using fx_to_jpy.
        Allows negative quantities (short positions, with UI warning).
        Empty DataFrame if input is empty.
    """
    if trades.empty:
        return pd.DataFrame(columns=[
            "ticker", "quantity", "avg_cost_jpy", "cost_basis_jpy", "realized_pnl_jpy"
        ])

    trades = trades.copy()
    trades["ticker"] = trades["ticker"].str.upper()

    # Pre-compute JPY amounts for each trade
    trades["gross"] = trades["quantity"] * trades["price"]
    trades["fees_jpy"] = trades["fees"] * trades["fx_to_jpy"]
    trades["gross_jpy"] = trades["gross"] * trades["fx_to_jpy"]

    result_rows = []
    
    # Group by ticker and process chronologically
    for ticker, group in trades.sort_values(["trade_date", "id"]).groupby("ticker", sort=False):
        qty = 0.0
        cost_basis = 0.0  # JPY
        realized = 0.0    # JPY

        for _, row in group.iterrows():
            q = float(row["quantity"])
            
            if row["side"] == "BUY":
                # BUY: Add cost and shares
                trade_cost = row["gross_jpy"] + row["fees_jpy"]
                qty += q
                cost_basis += trade_cost
                
            else:  # SELL
                # SELL: Realize P&L at current average cost
                if qty <= 0:
                    # Selling with no position (short); use 0 as avg cost
                    avg_cost = 0.0
                else:
                    avg_cost = cost_basis / qty

                proceeds = row["gross_jpy"] - row["fees_jpy"]
                cost_of_sold = avg_cost * q
                realized += (proceeds - cost_of_sold)

                qty -= q
                cost_basis -= cost_of_sold

        # Final position state per ticker
        avg_cost = (cost_basis / qty) if qty != 0 else 0.0
        result_rows.append({
            "ticker": ticker,
            "quantity": qty,
            "avg_cost_jpy": avg_cost,
            "cost_basis_jpy": cost_basis,
            "realized_pnl_jpy": realized,
        })

    return pd.DataFrame(result_rows)


# ============================================================================
# Market Data Fetching (Optional)
# ============================================================================


def try_fetch_price_yf(ticker: str) -> Optional[Tuple[float, str]]:
    """
    Attempt to fetch current price from yfinance.
    
    Best-effort function that returns None on any failure.
    Useful for mark-to-market calculations.
    
    Args:
        ticker: Stock ticker symbol.
                For Japanese stocks, may need .T suffix (e.g., 7203.T for Toyota)
                
    Returns:
        Tuple[float, str]: (price, currency_code) or None if fetch fails
        
    Note:
        Wrapped in try/except; returns None if yfinance not installed,
        network error, or ticker not found.
    """
    if not YF_OK:
        return None
        
    try:
        t = yf.Ticker(ticker)
        info = getattr(t, "fast_info", None)
        
        if info and "last_price" in info and info["last_price"] is not None:
            price = float(info["last_price"])
            currency = info.get("currency", "USD")
            return price, str(currency).upper()
        
        # Fallback to historical data
        hist = t.history(period="5d")
        if hist is None or hist.empty:
            return None
            
        price = float(hist["Close"].dropna().iloc[-1])
        return price, "USD"  # Default to USD if currency unknown
        
    except Exception:
        return None


# ============================================================================
# Streamlit UI Setup
# ============================================================================

st.set_page_config(page_title="Stock Journal (Local)", layout="wide")

# Initialize database on first load
init_db()

st.title("📒 Stock Journal (Local on Mac)")
st.caption(f"本地 SQLite + Streamlit。数据库: {DB_PATH} | 基准币种: {BASE_CCY}")

# Sidebar page selection
page = st.sidebar.radio("功能", [
    "➕ 录入交易",
    "📥 导入CSV",
    "📃 交易列表",
    "📦 持仓汇总",
    "📊 Dashboard",
    "💰 价格/汇率"
])


# ============================================================================
# Page: 录入交易 (Add Trade)
# ============================================================================

if page == "➕ 录入交易":
    st.subheader("录入一笔交易")
    
    with st.form("add_trade_form"):
        col1, col2, col3 = st.columns(3)
        trade_date = col1.date_input("日期", dt.date.today())
        ticker = col2.text_input("Ticker（例：AAPL / 7203.T）", value="").strip().upper()
        side = col3.selectbox("方向", ["BUY", "SELL"])

        col1, col2, col3, col4 = st.columns(4)
        quantity = col1.number_input("数量", min_value=0.0, value=1.0, step=1.0)
        price = col2.number_input("成交价（交易币种）", min_value=0.0, value=0.0, step=0.01)
        currency = col3.text_input("币种（JPY/USD）", value="JPY").strip().upper()
        fees = col4.number_input("手续费（交易币种）", min_value=0.0, value=0.0, step=0.01)

        fx_to_jpy = st.number_input(
            "fx_to_jpy（1币种=多少JPY；JPY填1）",
            min_value=0.0, value=1.0, step=0.1
        )
        note = st.text_input("备注（可选）", value="").strip()

        submitted = st.form_submit_button("💾 保存")
        
        if submitted:
            if not ticker:
                st.error("❌ Ticker 不能为空")
            elif quantity <= 0:
                st.error("❌ 数量必须 > 0")
            else:
                try:
                    conn = get_conn()
                    conn.execute("""
                        INSERT INTO trades (trade_date, ticker, side, quantity, price, currency, fees, fx_to_jpy, note)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        trade_date.isoformat(),
                        ticker,
                        side,
                        float(quantity),
                        float(price),
                        currency,
                        float(fees),
                        float(fx_to_jpy),
                        note if note else None
                    ))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ 已保存: {side} {quantity} {ticker} @ {price} {currency}")
                except Exception as e:
                    st.error(f"❌ 保存失败: {str(e)}")


# ============================================================================
# Page: 导入CSV (Import CSV)
# ============================================================================

elif page == "📥 导入CSV":
    st.subheader("导入 CSV（自定义格式）")
    st.write("你可以先导出券商的交易CSV，然后把列名映射到本工具字段。")
    st.info("📋 要求至少包含：trade_date, ticker, side, quantity, price, currency。"
            "fees/fx_to_jpy/note 可选。")

    upload = st.file_uploader("上传 CSV", type=["csv"])
    
    if upload:
        try:
            df = pd.read_csv(upload)
            st.write("📊 预览（前20行）：")
            st.dataframe(df.head(20), use_container_width=True)

            st.write("🔄 列名映射：")
            cols = list(df.columns)
            
            m1, m2, m3 = st.columns(3)
            c_date = m1.selectbox("trade_date 对应列", cols)
            c_ticker = m1.selectbox("ticker 对应列", cols)
            c_side = m1.selectbox("side 对应列", cols)

            c_qty = m2.selectbox("quantity 对应列", cols)
            c_price = m2.selectbox("price 对应列", cols)
            c_ccy = m2.selectbox("currency 对应列", cols)

            c_fees = m3.selectbox("fees（可选）", ["<none>"] + cols)
            c_fx = m3.selectbox("fx_to_jpy（可选）", ["<none>"] + cols)
            c_note = m3.selectbox("note（可选）", ["<none>"] + cols)

            if st.button("📥 导入到数据库"):
                try:
                    to_ins = pd.DataFrame()
                    to_ins["trade_date"] = pd.to_datetime(df[c_date]).dt.date.astype(str)
                    to_ins["ticker"] = df[c_ticker].astype(str).str.upper()
                    to_ins["side"] = df[c_side].astype(str).str.upper().replace({"B": "BUY", "S": "SELL"})
                    to_ins["quantity"] = df[c_qty].astype(float)
                    to_ins["price"] = df[c_price].astype(float)
                    to_ins["currency"] = df[c_ccy].astype(str).str.upper()
                    to_ins["fees"] = 0.0 if c_fees == "<none>" else df[c_fees].astype(float).fillna(0.0)
                    to_ins["fx_to_jpy"] = 1.0 if c_fx == "<none>" else df[c_fx].astype(float).fillna(1.0)
                    to_ins["note"] = None if c_note == "<none>" else df[c_note].astype(str)

                    conn = get_conn()
                    conn.executemany("""
                        INSERT INTO trades (trade_date, ticker, side, quantity, price, currency, fees, fx_to_jpy, note)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, list(to_ins.itertuples(index=False, name=None)))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ 导入完成！共 {len(to_ins)} 条")
                    
                except Exception as e:
                    st.error(f"❌ 导入失败: {str(e)}")
                    
        except Exception as e:
            st.error(f"❌ 读取 CSV 失败: {str(e)}")


# ============================================================================
# Page: 交易列表 (Trade List)
# ============================================================================

elif page == "📃 交易列表":
    st.subheader("交易列表")
    trades = read_trades()
    
    if trades.empty:
        st.warning("⚠️ 还没有交易记录。")
    else:
        # Display options
        col1, col2 = st.columns([2, 1])
        with col1:
            filter_ticker = st.text_input("按 Ticker 筛选（留空显示全部）", value="").strip().upper()
        with col2:
            limit = st.number_input("显示最多行数", min_value=1, value=100)

        if filter_ticker:
            display_trades = trades[trades["ticker"] == filter_ticker].head(limit)
        else:
            display_trades = trades.head(limit)

        st.dataframe(display_trades, use_container_width=True)
        st.info(f"📊 共显示 {len(display_trades)} 条交易")


# ============================================================================
# Page: 持仓汇总 (Position Summary)
# ============================================================================

elif page == "📦 持仓汇总":
    st.subheader("持仓汇总（JPY 口径）")
    
    trades = read_trades()
    pos = compute_positions(trades)
    
    if pos.empty:
        st.warning("⚠️ 还没有交易记录。")
    else:
        prices = read_prices()
        prices_map = {r["ticker"]: r for _, r in prices.iterrows()} if not prices.empty else {}

        rows = []
        for _, r in pos.iterrows():
            t = r["ticker"]
            qty = float(r["quantity"])
            avg_cost = float(r["avg_cost_jpy"])
            cost_basis = float(r["cost_basis_jpy"])
            realized = float(r["realized_pnl_jpy"])

            # Mark-to-market using latest prices
            mtm_jpy = np.nan
            last_price_info = prices_map.get(t)

            if last_price_info is not None:
                p = float(last_price_info["price"])
                fx = float(last_price_info["fx_to_jpy"])
                mtm_jpy = jpy_value(p, qty, fx)

            unrealized = (mtm_jpy - cost_basis) if not np.isnan(mtm_jpy) else np.nan

            rows.append({
                "ticker": t,
                "数量": qty,
                "均成本(JPY)": avg_cost,
                "成本(JPY)": cost_basis,
                "市值(JPY)": mtm_jpy,
                "已实现(JPY)": realized,
                "未实现(JPY)": unrealized,
            })

        out = pd.DataFrame(rows).sort_values("市值(JPY)", ascending=False, na_position="last")
        st.dataframe(out, use_container_width=True)

        if (out["数量"] < 0).any():
            st.warning("⚠️ 检测到负持仓（先卖后买/做空）。如果这是不想要的，请检查导入/录入数据。")


# ============================================================================
# Page: Dashboard
# ============================================================================

elif page == "📊 Dashboard":
    st.subheader("Dashboard - 资产与收益概览")
    
    trades = read_trades()
    
    if trades.empty:
        st.warning("⚠️ 还没有交易记录。")
    else:
        pos = compute_positions(trades)
        prices = read_prices()
        prices_map = {r["ticker"]: r for _, r in prices.iterrows()} if not prices.empty else {}

        # Calculate totals
        total_cost = float(pos["cost_basis_jpy"].sum())
        total_realized = float(pos["realized_pnl_jpy"].sum())

        total_mkt = 0.0
        has_mkt = False
        for _, r in pos.iterrows():
            t = r["ticker"]
            qty = float(r["quantity"])
            pinfo = prices_map.get(t)
            if pinfo is None:
                continue
            total_mkt += jpy_value(float(pinfo["price"]), qty, float(pinfo["fx_to_jpy"]))
            has_mkt = True

        # KPI metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("持仓成本（JPY）", f"{total_cost:,.0f}")
        c2.metric("已实现损益（JPY）", f"{total_realized:,.0f}")
        
        if has_mkt:
            total_unrealized = total_mkt - total_cost
            total_return_pct = ((total_realized + total_unrealized) / (total_cost or 1)) * 100 if total_cost > 0 else 0
            c3.metric("未实现损益（JPY）", f"{total_unrealized:,.0f}")
            st.metric("总收益率 %", f"{total_return_pct:.2f}%")
        else:
            c3.metric("未实现损益（JPY）", "—（先录入价格）")

        st.divider()
        st.write("📊 按 Ticker 的已实现损益：")
        realized_df = pos[["ticker", "realized_pnl_jpy"]].sort_values("realized_pnl_jpy", ascending=False)
        st.dataframe(realized_df, use_container_width=True)


# ============================================================================
# Page: 价格/汇率 (Price/FX Management)
# ============================================================================

elif page == "💰 价格/汇率":
    st.subheader("价格/汇率（用于计算未实现损益）")
    st.caption("你可以手动维护每个 ticker 的最新价格；也可以尝试用 yfinance 自动拉取（best-effort）。")

    col1, col2 = st.columns([2, 1])

    with col1:
        ticker = st.text_input("Ticker", value="").strip().upper()
        asof = st.date_input("日期（asof）", value=dt.date.today())

    with col2:
        mode = st.selectbox("方式", ["手动输入", "尝试自动拉取(yfinance)"])

    if mode == "手动输入":
        c1, c2, c3 = st.columns(3)
        price = c1.number_input("最新价格（交易币种）", min_value=0.0, value=0.0, step=0.01)
        currency = c2.text_input("币种（JPY/USD）", value="JPY").strip().upper()
        fx = c3.number_input("fx_to_jpy（JPY填1）", min_value=0.0, value=1.0, step=0.1)
        
        if st.button("💾 保存价格"):
            if not ticker:
                st.error("❌ Ticker 不能为空")
            else:
                try:
                    upsert_price(ticker, price, currency, fx, asof.isoformat())
                    st.success(f"✅ 已保存 {ticker} 价格")
                except Exception as e:
                    st.error(f"❌ 保存失败: {str(e)}")

    else:  # Auto-fetch mode
        if not YF_OK:
            st.error("❌ 当前环境无法使用 yfinance（可能没装好或被网络限制）。"
                    "你可以用手动输入，或运行: pip install yfinance")
        else:
            fx = st.number_input(
                "fx_to_jpy（如果拉到的是USD价格，这里填USD->JPY；日股可填1）",
                min_value=0.0, value=150.0, step=0.1
            )
            if st.button("🔄 自动拉取并保存"):
                if not ticker:
                    st.error("❌ Ticker 不能为空")
                else:
                    with st.spinner("🔄 拉取中..."):
                        res = try_fetch_price_yf(ticker)
                        if res is None:
                            st.error("❌ 拉取失败：请检查 ticker（比如日股是否需要 .T）,"
                                   "或检查网络连接，或改用手动输入。")
                        else:
                            price, currency = res
                            try:
                                upsert_price(ticker, price, currency, fx, asof.isoformat())
                                st.success(f"✅ 已保存 {ticker} 价格 = {price} {currency}")
                            except Exception as e:
                                st.error(f"❌ 保存失败: {str(e)}")

    st.divider()
    st.write("📋 当前已维护的价格：")
    prices = read_prices()
    if prices.empty:
        st.info("ℹ️ 暂无价格记录")
    else:
        st.dataframe(prices, use_container_width=True)
