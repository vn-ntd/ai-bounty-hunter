import sqlite3
import json
from datetime import datetime, timezone
from typing import Optional, List
from bounty_hunter.models import Bounty, BountyStatus, FinancialRecord, FinancialSummary

class FinancialLedger:
    """SQLite-backed financial ledger tracking expenses, bounty earnings and monthly goal progress."""

    def __init__(self, db_path: str = "bounty_ledger.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS financial_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_type TEXT NOT NULL,
                    amount_usd REAL NOT NULL,
                    description TEXT NOT NULL,
                    bounty_id TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bounties (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    repository TEXT NOT NULL,
                    reward_usd REAL NOT NULL,
                    description TEXT,
                    language TEXT,
                    status TEXT NOT NULL,
                    labels TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def record_spend(self, amount_usd: float, description: str, bounty_id: Optional[str] = None) -> FinancialRecord:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO financial_records (record_type, amount_usd, description, bounty_id, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, ("SPEND", amount_usd, description, bounty_id, now_iso))
            conn.commit()
            rec_id = cursor.lastrowid
        return FinancialRecord(
            id=rec_id,
            record_type="SPEND",
            amount_usd=amount_usd,
            description=description,
            bounty_id=bounty_id,
            timestamp=datetime.fromisoformat(now_iso)
        )

    def record_earning(self, amount_usd: float, description: str, bounty_id: Optional[str] = None) -> FinancialRecord:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO financial_records (record_type, amount_usd, description, bounty_id, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, ("EARN", amount_usd, description, bounty_id, now_iso))
            conn.commit()
            rec_id = cursor.lastrowid
        return FinancialRecord(
            id=rec_id,
            record_type="EARN",
            amount_usd=amount_usd,
            description=description,
            bounty_id=bounty_id,
            timestamp=datetime.fromisoformat(now_iso)
        )

    def get_records(self) -> List[FinancialRecord]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM financial_records ORDER BY id ASC").fetchall()
            return [
                FinancialRecord(
                    id=row["id"],
                    record_type=row["record_type"],
                    amount_usd=row["amount_usd"],
                    description=row["description"],
                    bounty_id=row["bounty_id"],
                    timestamp=datetime.fromisoformat(row["timestamp"])
                ) for row in rows
            ]

    def save_bounty(self, bounty: Bounty) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO bounties (id, title, url, source, repository, reward_usd, description, language, status, labels, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    reward_usd=excluded.reward_usd,
                    status=excluded.status,
                    labels=excluded.labels
            """, (
                bounty.id,
                bounty.title,
                bounty.url,
                bounty.source,
                bounty.repository,
                bounty.reward_usd,
                bounty.description,
                bounty.language,
                bounty.status.value,
                json.dumps(bounty.labels),
                bounty.created_at.isoformat()
            ))
            conn.commit()

    def update_bounty_status(self, bounty_id: str, status: BountyStatus) -> None:
        with self._get_connection() as conn:
            conn.execute("UPDATE bounties SET status = ? WHERE id = ?", (status.value, bounty_id))
            conn.commit()

    def get_bounties(self) -> List[Bounty]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM bounties ORDER BY reward_usd DESC").fetchall()
            bounties = []
            for row in rows:
                labels = json.loads(row["labels"]) if row["labels"] else []
                bounties.append(Bounty(
                    id=row["id"],
                    title=row["title"],
                    url=row["url"],
                    source=row["source"],
                    repository=row["repository"],
                    reward_usd=row["reward_usd"],
                    description=row["description"] or "",
                    language=row["language"] or "Unknown",
                    status=BountyStatus(row["status"]),
                    labels=labels,
                    created_at=datetime.fromisoformat(row["created_at"])
                ))
            return bounties

    def get_summary(self, days_elapsed: int = 1) -> FinancialSummary:
        records = self.get_records()
        total_earned = sum(r.amount_usd for r in records if r.record_type == "EARN")
        total_spent = sum(r.amount_usd for r in records if r.record_type == "SPEND")
        net_profit = round(total_earned - total_spent, 2)
        
        target_usd = 100.0
        progress_percent = round(min(100.0, (total_earned / target_usd) * 100.0), 1)
        runway_days = max(0, 30 - days_elapsed)

        bounties = self.get_bounties()
        solved_statuses = {BountyStatus.SOLVED, BountyStatus.PR_SUBMITTED, BountyStatus.MERGED, BountyStatus.PAID}
        solved_count = sum(1 for b in bounties if b.status in solved_statuses)

        return FinancialSummary(
            total_earned_usd=round(total_earned, 2),
            total_spent_usd=round(total_spent, 2),
            net_profit_usd=net_profit,
            target_usd=target_usd,
            target_progress_percent=progress_percent,
            runway_days_remaining=runway_days,
            bounties_solved_count=solved_count
        )
