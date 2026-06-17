"""
SQLite wrapper for the news aggregator.

Single-file DB at NEWS_DB_PATH (default /var/lib/claude-news/db.sqlite).
All access is through prepared statements. The DB object is intentionally
trivial — concurrency is handled by SQLite's WAL mode plus serializing
writes from the scheduler (only one refresh runs at a time).
"""

import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

DEFAULT_DB_PATH = "/var/lib/claude-news/db.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  link TEXT NOT NULL,
  summary TEXT,
  source_domain TEXT NOT NULL,
  source_category TEXT NOT NULL,
  pub_date TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  UNIQUE(link, source_category)
);
CREATE INDEX IF NOT EXISTS idx_items_pub_date ON items(pub_date);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(source_category);
CREATE INDEX IF NOT EXISTS idx_items_source ON items(source_domain);

CREATE TABLE IF NOT EXISTS feed_status (
  feed_url TEXT PRIMARY KEY,
  last_fetched_at TEXT,
  last_status TEXT,
  last_error TEXT,
  items_in_last_fetch INTEGER
);
"""


class DB:
    def __init__(self, path=None):
        self.path = path or os.environ.get("NEWS_DB_PATH", DEFAULT_DB_PATH)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._write_lock = threading.Lock()
        with self._conn() as c:
            c.executescript(SCHEMA)
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("PRAGMA synchronous=NORMAL")

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def insert_items(self, items):
        if not items:
            return 0
        # Note: pub_date is intentionally NOT updated on conflict — the
        # original publication date should not drift on subsequent refreshes.
        # Otherwise feeds that omit pub_date (we previously fell back to
        # fetched_at) would keep getting bumped to "now" every 20 minutes,
        # making week-old articles permanently rank as fresh.
        sql = """
            INSERT INTO items
              (id, title, link, summary, source_domain, source_category, pub_date, fetched_at)
            VALUES
              (:id, :title, :link, :summary, :source_domain, :source_category, :pub_date, :fetched_at)
            ON CONFLICT(id) DO UPDATE SET
              title=excluded.title,
              summary=excluded.summary
        """
        with self._write_lock, self._conn() as c:
            before = c.execute("SELECT COUNT(*) FROM items").fetchone()[0]
            c.executemany(sql, items)
            after = c.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        return after - before

    def get_items(self, category=None, hours_back=48, source=None, query=None, limit=30):
        where = []
        params = {}
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).isoformat()
        where.append("pub_date >= :cutoff")
        params["cutoff"] = cutoff
        if category:
            where.append("source_category = :category")
            params["category"] = category
        if source:
            where.append("source_domain = :source")
            params["source"] = source
        if query:
            where.append("(LOWER(title) LIKE :q OR LOWER(IFNULL(summary, '')) LIKE :q)")
            params["q"] = f"%{query.lower()}%"
        sql = f"""
            SELECT id, title, link, summary, source_domain, source_category, pub_date
            FROM items
            WHERE {' AND '.join(where)}
            ORDER BY pub_date DESC
            LIMIT :limit
        """
        params["limit"] = int(limit)
        with self._conn() as c:
            rows = c.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def count_items(self):
        with self._conn() as c:
            return c.execute("SELECT COUNT(*) FROM items").fetchone()[0]

    def last_refresh(self):
        with self._conn() as c:
            row = c.execute(
                "SELECT MAX(last_fetched_at) FROM feed_status WHERE last_status = 'ok'"
            ).fetchone()
        return row[0] if row and row[0] else None

    def upsert_feed_status(self, feed_url, status, error=None, items_count=0):
        now = datetime.now(timezone.utc).isoformat()
        sql = """
            INSERT INTO feed_status
              (feed_url, last_fetched_at, last_status, last_error, items_in_last_fetch)
            VALUES (:feed_url, :ts, :status, :error, :items)
            ON CONFLICT(feed_url) DO UPDATE SET
              last_fetched_at=excluded.last_fetched_at,
              last_status=excluded.last_status,
              last_error=excluded.last_error,
              items_in_last_fetch=excluded.items_in_last_fetch
        """
        with self._write_lock, self._conn() as c:
            c.execute(sql, {
                "feed_url": feed_url,
                "ts": now,
                "status": status,
                "error": error,
                "items": items_count,
            })

    def repair_pub_dates_from_link(self):
        """
        One-shot migration: for items whose pub_date equals fetched_at (i.e.
        we never had a real publication date and fell back to "now"), try to
        recover the actual date from the URL path (matches /YYYY-MM-DD/).
        Returns the number of rows updated.
        """
        import re as _re
        url_date_re = _re.compile(r"/(20\d{2})[-/](\d{1,2})[-/](\d{1,2})(?:/|$)")
        fixed = 0
        with self._write_lock, self._conn() as c:
            rows = c.execute(
                "SELECT id, link, pub_date, fetched_at FROM items WHERE pub_date = fetched_at"
            ).fetchall()
            for r in rows:
                m = url_date_re.search(r["link"] or "")
                if not m:
                    continue
                try:
                    y, mo, d = (int(x) for x in m.groups())
                    if not (1 <= mo <= 12 and 1 <= d <= 31):
                        continue
                    new_pub = f"{y:04d}-{mo:02d}-{d:02d}T12:00:00+00:00"
                    c.execute(
                        "UPDATE items SET pub_date = ? WHERE id = ?",
                        (new_pub, r["id"]),
                    )
                    fixed += 1
                except Exception:
                    continue
        return fixed

    def get_sources_status(self):
        from feeds import FEEDS
        with self._conn() as c:
            status_rows = {
                r["feed_url"]: dict(r)
                for r in c.execute("SELECT * FROM feed_status").fetchall()
            }
        out = []
        for f in FEEDS:
            s = status_rows.get(f["url"], {})
            out.append({
                "url": f["url"],
                "domain": f["domain"],
                "category": f["category"],
                "last_fetched_at": s.get("last_fetched_at"),
                "last_status": s.get("last_status"),
                "last_error": s.get("last_error"),
                "items_in_last_fetch": s.get("items_in_last_fetch", 0),
            })
        return out
