"""SQLite 榜单历史:记录快照,筛出新上榜项目。"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from scraper import Repo

DB_PATH = Path(os.environ.get("TR_DB_PATH", Path(__file__).parent / "data" / "history.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS sightings (
    full_name   TEXT NOT NULL,
    date        TEXT NOT NULL,
    stars       INTEGER DEFAULT 0,
    stars_today INTEGER DEFAULT 0,
    PRIMARY KEY (full_name, date)
);
"""


def _connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    return conn


def filter_new(repos: list[Repo], date: str, lookback_days: int = 14,
               db_path: Path = DB_PATH) -> list[Repo]:
    """返回近 lookback_days 天内(不含今天)没上过榜的 repo。"""
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT DISTINCT full_name FROM sightings "
            "WHERE date < ? AND date >= date(?, ?)",
            (date, date, f"-{lookback_days} days"),
        ).fetchall()
    seen = {r[0] for r in rows}
    return [r for r in repos if r.full_name not in seen]


def find_surges(repos: list[Repo], date: str, lookback_days: int = 7,
                ratio: float = 1.5, db_path: Path = DB_PATH) -> list[Repo]:
    """在已上过榜的 repo 里,找当前 star 相比近 lookback_days 天内
    最近一次记录暴涨 ≥ ratio 倍的,标记 is_surge 并返回。"""
    surges: list[Repo] = []
    with _connect(db_path) as conn:
        for repo in repos:
            row = conn.execute(
                "SELECT stars FROM sightings "
                "WHERE full_name = ? AND date < ? AND date >= date(?, ?) "
                "ORDER BY date DESC LIMIT 1",
                (repo.full_name, date, date, f"-{lookback_days} days"),
            ).fetchone()
            if row and row[0] > 0 and repo.stars >= row[0] * ratio:
                repo.is_surge = True
                surges.append(repo)
    return surges


def record(repos: list[Repo], date: str, db_path: Path = DB_PATH) -> None:
    """幂等写入当日快照。"""
    with _connect(db_path) as conn:
        conn.executemany(
            "INSERT OR REPLACE INTO sightings (full_name, date, stars, stars_today) "
            "VALUES (?, ?, ?, ?)",
            [(r.full_name, date, r.stars, r.stars_today) for r in repos],
        )
        conn.commit()
