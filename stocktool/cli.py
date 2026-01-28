"""
DEPRECATED: Legacy Typer CLI module (kept for backwards compatibility)

This module is no longer the primary interface for StockAnalysis.
Please use the Streamlit Web UI instead:
  streamlit run stocktool/app.py

The new architecture uses:
- stocktool/app.py: Streamlit UI layer
- stocktool/db.py: SQLite management (raw sqlite3)
- No longer uses SQLModel or Typer
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from tabulate import tabulate

from stocktool import __version__
from stocktool.db import get_engine, init_db, session_scope
from stocktool.models import Side
from stocktool.services.portfolio import compute_positions, summarize_positions
from stocktool.services.trades import add_trade, all_trades, list_trades

app = typer.Typer(help="Local stock journal and analysis tool.")


def _engine_from_option(db: Optional[Path]):
    return get_engine(db)


@app.callback()
def main(
    ctx: typer.Context,
    db: Optional[Path] = typer.Option(
        None,
        "--db",
        help="Path to sqlite file (default: ./data/stocktool.db).",
        dir_okay=True,
        file_okay=True,
        writable=True,
    ),
):
    ctx.obj = {"engine": _engine_from_option(db)}


@app.command()
def init(ctx: typer.Context):
    """Create the database and tables."""
    engine = ctx.obj["engine"]
    engine = init_db(engine)
    typer.echo(f"Database initialized at {engine.url.database}")


@app.command()
def add(
    symbol: str = typer.Argument(..., help="Ticker symbol"),
    side: Side = typer.Argument(..., help="buy or sell"),
    quantity: float = typer.Argument(..., help="Number of shares"),
    price: float = typer.Argument(..., help="Fill price"),
    fee: float = typer.Option(0.0, help="Commission/fees"),
    when: Optional[datetime] = typer.Option(None, help="Fill datetime (ISO, defaults to now UTC)"),
    account: Optional[str] = typer.Option(None, help="Account label"),
    note: Optional[str] = typer.Option(None, help="Free-form note"),
    ctx: typer.Context,
):
    engine = ctx.obj["engine"]
    init_db(engine)
    with session_scope(engine) as session:
        trade = add_trade(
            session,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            fee=fee,
            when=when,
            account=account,
            note=note,
        )
    typer.echo(f"Recorded trade #{trade.id}: {trade.side} {trade.quantity} {trade.symbol} @ {trade.price}")


@app.command("list")
def list_cmd(
    symbol: Optional[str] = typer.Option(None, help="Filter by symbol"),
    account: Optional[str] = typer.Option(None, help="Filter by account"),
    limit: int = typer.Option(50, help="Max rows"),
    ctx: typer.Context,
):
    engine = ctx.obj["engine"]
    init_db(engine)
    with session_scope(engine) as session:
        trades = list_trades(session, symbol=symbol, limit=limit, account=account)
    if not trades:
        typer.echo("No trades yet.")
        raise typer.Exit()
    table = [
        [
            t.id,
            t.datetime.isoformat(timespec="seconds"),
            t.symbol,
            t.side.value,
            t.quantity,
            t.price,
            t.fee,
            t.account or "",
            t.note or "",
        ]
        for t in trades
    ]
    typer.echo(tabulate(table, headers=["id", "datetime", "symbol", "side", "qty", "price", "fee", "account", "note"]))


@app.command()
def positions(ctx: typer.Context):
    """Show average cost, quantity, and realized PnL per symbol."""
    engine = ctx.obj["engine"]
    init_db(engine)
    with session_scope(engine) as session:
        trades = list(all_trades(session))
    pos_map = compute_positions(trades)
    positions = summarize_positions(pos_map)
    if not positions:
        typer.echo("No positions yet.")
        raise typer.Exit()
    table = [
        [
            p.symbol,
            round(p.quantity, 4),
            round(p.avg_cost, 4),
            round(p.invested, 2),
            round(p.realized_pnl, 2),
        ]
        for p in positions
    ]
    typer.echo(tabulate(table, headers=["symbol", "qty", "avg_cost", "invested", "realized_pnl"]))


@app.command()
def version():
    """Print version."""
    typer.echo(__version__)


if __name__ == "__main__":
    app()
