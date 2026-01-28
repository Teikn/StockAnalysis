from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List

from stocktool.models import Side, Trade


@dataclass
class Position:
    symbol: str
    quantity: float = 0.0
    avg_cost: float = 0.0
    invested: float = 0.0  # Total capital put in (buys - sells proceeds)
    realized_pnl: float = 0.0

    @property
    def market_value(self) -> float:
        # Requires price; left as 0 by default.
        return 0.0


def compute_positions(trades: Iterable[Trade]) -> Dict[str, Position]:
    positions: Dict[str, Position] = defaultdict(lambda: Position(symbol=""))
    for trade in trades:
        symbol = trade.symbol.upper()
        pos = positions[symbol]
        if not pos.symbol:
            pos.symbol = symbol

        if trade.side == Side.BUY:
            new_qty = pos.quantity + trade.quantity
            if new_qty == 0:
                pos.avg_cost = 0
            else:
                pos.avg_cost = (pos.avg_cost * pos.quantity + trade.price * trade.quantity + trade.fee) / new_qty
            pos.quantity = new_qty
            pos.invested += trade.price * trade.quantity + trade.fee
        else:  # SELL
            sell_qty = min(trade.quantity, pos.quantity) if pos.quantity > 0 else trade.quantity
            pos.realized_pnl += (trade.price - pos.avg_cost) * sell_qty - trade.fee
            pos.quantity -= trade.quantity
            pos.invested -= trade.price * trade.quantity - trade.fee
            if pos.quantity <= 0:
                pos.avg_cost = 0.0
    return positions


def summarize_positions(positions: Dict[str, Position]) -> List[Position]:
    return list(positions.values())
