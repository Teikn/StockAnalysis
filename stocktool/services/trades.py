from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from sqlmodel import Session, select

from stocktool.models import Side, Trade


def add_trade(
    session: Session,
    *,
    symbol: str,
    side: Side,
    quantity: float,
    price: float,
    fee: float = 0.0,
    when: Optional[datetime] = None,
    account: Optional[str] = None,
    note: Optional[str] = None,
) -> Trade:
    trade = Trade(
        symbol=symbol.upper(),
        side=side,
        quantity=quantity,
        price=price,
        fee=fee,
        datetime=when or datetime.utcnow(),
        account=account,
        note=note,
    )
    session.add(trade)
    session.commit()
    session.refresh(trade)
    return trade


def list_trades(
    session: Session,
    *,
    symbol: Optional[str] = None,
    limit: Optional[int] = 50,
    account: Optional[str] = None,
) -> List[Trade]:
    query = select(Trade).order_by(Trade.datetime.desc())
    if symbol:
        query = query.where(Trade.symbol == symbol.upper())
    if account:
        query = query.where(Trade.account == account)
    if limit:
        query = query.limit(limit)
    return list(session.exec(query))


def all_trades(session: Session) -> Iterable[Trade]:
    return session.exec(select(Trade).order_by(Trade.datetime))
