from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


class Trade(SQLModel, table=True):
    """
    Basic trade record.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True, max_length=16)
    side: Side
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
    fee: float = Field(default=0.0, ge=0)
    datetime: datetime = Field(default_factory=datetime.utcnow, index=True)
    account: Optional[str] = Field(default=None, max_length=64, index=True)
    note: Optional[str] = Field(default=None)


# Convenience type hints
__all__ = ["Trade", "Side"]
