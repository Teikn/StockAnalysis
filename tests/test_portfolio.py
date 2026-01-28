from datetime import datetime

from sqlmodel import Session, select

from stocktool.db import init_db
from stocktool.models import Side, Trade
from stocktool.services.portfolio import compute_positions


def test_positions_average_cost(tmp_path):
    engine = init_db(tmp_path / "test.db")
    with Session(engine) as session:
        session.add_all(
            [
                Trade(symbol="AAPL", side=Side.BUY, quantity=10, price=100, datetime=datetime(2024, 1, 1)),
                Trade(symbol="AAPL", side=Side.BUY, quantity=10, price=110, datetime=datetime(2024, 1, 2)),
                Trade(symbol="AAPL", side=Side.SELL, quantity=5, price=120, datetime=datetime(2024, 1, 3)),
            ]
        )
        session.commit()

        positions = compute_positions(session.exec(select(Trade)))
        aapl = positions["AAPL"]
        assert round(aapl.quantity, 2) == 15
        assert round(aapl.avg_cost, 2) == 105.0
        assert round(aapl.realized_pnl, 2) == 75.0  # (120-105)*5
