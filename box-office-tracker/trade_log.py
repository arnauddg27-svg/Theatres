"""
Trade Logger — SQLite persistence for box office trades.
"""

import os
import sqlite3
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DATA_DIR, "trades.db")


class TradeLog:
    def __init__(self, db_path: str = DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS box_office_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie TEXT NOT NULL,
                bracket_question TEXT,
                bracket_low REAL,
                bracket_high REAL,
                our_implied_prob REAL,
                market_price REAL,
                edge REAL,
                token_id TEXT,
                market_id TEXT,
                order_size REAL,
                order_price REAL,
                order_cost REAL,
                order_id TEXT,
                status TEXT DEFAULT 'placed',
                pnl REAL,
                prediction_mid REAL,
                prediction_low REAL,
                prediction_high REAL,
                created_at TEXT DEFAULT (datetime('now')),
                settled_at TEXT
            );
        """)
        self.conn.commit()

    def record_trade(self, movie: str, bracket_question: str,
                     bracket_low: float, bracket_high: float,
                     our_prob: float, market_price: float, edge: float,
                     token_id: str, market_id: str,
                     size: float, price: float, cost: float,
                     order_id: str = "", status: str = "placed",
                     pred_mid: float = 0, pred_low: float = 0,
                     pred_high: float = 0) -> int:
        cur = self.conn.execute(
            """INSERT INTO box_office_trades
               (movie, bracket_question, bracket_low, bracket_high,
                our_implied_prob, market_price, edge, token_id, market_id,
                order_size, order_price, order_cost, order_id, status,
                prediction_mid, prediction_low, prediction_high)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (movie, bracket_question, bracket_low, bracket_high,
             our_prob, market_price, edge, token_id, market_id,
             size, price, cost, order_id, status,
             pred_mid, pred_low, pred_high),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_open_trades(self, movie: str = None) -> list[dict]:
        if movie:
            rows = self.conn.execute(
                "SELECT * FROM box_office_trades WHERE status='placed' AND movie=?",
                (movie,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM box_office_trades WHERE status='placed'"
            ).fetchall()
        return [dict(r) for r in rows]

    def has_traded_movie(self, movie: str) -> bool:
        """Check if we already have open trades for this movie this week."""
        row = self.conn.execute(
            """SELECT COUNT(*) as cnt FROM box_office_trades
               WHERE movie=? AND status='placed'
               AND created_at > datetime('now', '-7 days')""",
            (movie,),
        ).fetchone()
        return row["cnt"] > 0

    def settle_trade(self, trade_id: int, pnl: float):
        self.conn.execute(
            """UPDATE box_office_trades
               SET status='settled', pnl=?, settled_at=datetime('now')
               WHERE id=?""",
            (pnl, trade_id),
        )
        self.conn.commit()

    def recent_trades(self, limit: int = 20) -> list[dict]:
        rows = self.conn.execute(
            """SELECT * FROM box_office_trades
               ORDER BY created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def total_pnl(self) -> float:
        row = self.conn.execute(
            "SELECT COALESCE(SUM(pnl), 0) as total FROM box_office_trades WHERE status='settled'"
        ).fetchone()
        return row["total"]

    def close(self):
        self.conn.close()
