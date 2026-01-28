"""
Database initialization and connection management for StockAnalysis.

Uses raw sqlite3 with proper context management and foreign key enforcement.
Database file location: project_root/stocktool/portfolio.db
"""

import sqlite3
from pathlib import Path

# Database path: stocktool/portfolio.db
DB_PATH = Path(__file__).parent / "portfolio.db"


def get_conn() -> sqlite3.Connection:
    """
    Get a database connection with foreign keys enabled.
    
    Returns:
        sqlite3.Connection: Database connection with PRAGMA foreign_keys = ON
        
    Note:
        Always close the connection when done: conn.close()
        Or use in a context manager for automatic cleanup.
    """
    conn = sqlite3.connect(str(DB_PATH))
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """
    Initialize the database schema.
    
    Creates two tables if they don't exist:
    - trades: Atomic trade records with fees, currency, FX rate
    - prices: Latest prices per ticker for mark-to-market calculations
    
    Idempotent: Safe to call multiple times.
    """
    conn = get_conn()
    cur = conn.cursor()

    # Create trades table
    # All amounts stored in original currency; fx_to_jpy used for JPY conversion
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trade_date TEXT NOT NULL,                 -- YYYY-MM-DD format
        ticker TEXT NOT NULL,                     -- Stock ticker symbol (uppercase)
        side TEXT NOT NULL CHECK (side IN ('BUY','SELL')),
        quantity REAL NOT NULL CHECK (quantity > 0),
        price REAL NOT NULL CHECK (price >= 0),   -- Price in trade currency
        currency TEXT NOT NULL,                   -- e.g., JPY, USD
        fees REAL NOT NULL DEFAULT 0,             -- Fees in trade currency
        fx_to_jpy REAL NOT NULL DEFAULT 1,        -- Exchange rate: 1 unit of currency = fx_to_jpy JPY
        note TEXT                                  -- Optional memo/reference
    );
    """)

    # Index for common queries
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_ticker ON trades(ticker);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(trade_date);")

    # Create prices table for mark-to-market calculations
    # Stores the latest known price per ticker
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        ticker TEXT PRIMARY KEY,
        price REAL NOT NULL,                  -- Latest price in ticker's trading currency
        currency TEXT NOT NULL,               -- Currency of the price (USD, JPY, etc)
        fx_to_jpy REAL NOT NULL DEFAULT 1,    -- Current exchange rate to JPY
        asof TEXT NOT NULL                    -- Date price is valid for (YYYY-MM-DD)
    );
    """)

    conn.commit()
    conn.close()


def upsert_price(
    ticker: str,
    price: float,
    currency: str,
    fx_to_jpy: float,
    asof: str
) -> None:
    """
    Insert or update a price record.
    
    Uses INSERT ... ON CONFLICT pattern for upsert functionality.
    
    Args:
        ticker: Stock ticker symbol (will be uppercase)
        price: Latest price in trading currency
        currency: Currency code (e.g., 'USD', 'JPY')
        fx_to_jpy: Exchange rate (1 unit of currency = fx_to_jpy JPY)
        asof: Date the price is valid for (YYYY-MM-DD)
    """
    conn = get_conn()
    conn.execute("""
        INSERT INTO prices (ticker, price, currency, fx_to_jpy, asof)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(ticker) DO UPDATE SET
            price=excluded.price,
            currency=excluded.currency,
            fx_to_jpy=excluded.fx_to_jpy,
            asof=excluded.asof
    """, (ticker.upper(), float(price), currency.upper(), float(fx_to_jpy), asof))
    conn.commit()
    conn.close()
