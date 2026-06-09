"""
RSS/Atom feed fetching and normalization.
"""

import hashlib
import logging
import re
import socket
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
from dateutil import parser as dateparser

from feeds import unique_feed_urls, categories_for_url

log = logging.getLogger("feed_fetcher")

USER_AGENT = "ClaudeNewsAggregator/1.0 (+sslip.io)"

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _strip_html(text):
    if not text:
        return ""
    no_tags = _HTML_TAG_RE.sub(" ", text)
    return _WHITESPACE_RE.sub(" ", no_tags).strip()


def _to_utc_iso(value):
    if value is None:
        return None
    try:
        if hasattr(value, "tm_year"):
            dt = datetime(*value[:6], tzinfo=timezone.utc)
            return dt.isoformat()
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc).isoformat()
        if isinstance(value, str):
            try:
                dt = parsedate_to_datetime(value)
            except (TypeError, ValueError):
                dt = dateparser.parse(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
    except Exception as e:
        log.debug("date parse failed for %r: %s", value, e)
    return None


def fetch_feed(url, timeout=15):
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        parsed = feedparser.parse(
            url,
            agent=USER_AGENT,
            request_headers={"User-Agent": USER_AGENT},
        )
    finally:
        socket.setdefaulttimeout(old_timeout)

    if parsed.bozo and isinstance(parsed.bozo_exception, (OSError, socket.error)):
        raise parsed.bozo_exception

    items = []
    for entry in parsed.entries:
        link = (entry.get("link") or "").strip()
        title = (entry.get("title") or "").strip()
        if not link or not title:
            continue
        pub_date = (
            _to_utc_iso(entry.get("published_parsed"))
            or _to_utc_iso(entry.get("updated_parsed"))
            or _to_utc_iso(entry.get("published"))
            or _to_utc_iso(entry.get("updated"))
        )
        summary_raw = entry.get("summary") or entry.get("description") or ""
        if not summary_raw and entry.get("content"):
            try:
                summary_raw = entry["content"][0].get("value", "")
            except (IndexError, AttributeError):
                summary_raw = ""
        summary = _strip_html(summary_raw)[:2000]
        items.append({
            "link": link,
            "title": title,
            "summary": summary,
            "pub_date": pub_date,
        })
    return items


def _make_id(link, category):
    h = hashlib.sha256()
    h.update(link.encode("utf-8"))
    h.update(b"|")
    h.update(category.encode("utf-8"))
    return h.hexdigest()


def refresh_all_feeds(db):
    feeds_ok = 0
    feeds_error = 0
    items_inserted = 0

    for url in unique_feed_urls():
        try:
            raw_items = fetch_feed(url)
        except Exception as e:
            log.warning("feed fetch failed: %s — %s", url, e)
            db.upsert_feed_status(url, "error", error=str(e)[:500], items_count=0)
            feeds_error += 1
            continue

        rows = []
        fetched_at = datetime.now(timezone.utc).isoformat()
        for category, domain in categories_for_url(url):
            for it in raw_items:
                pub = it["pub_date"] or fetched_at
                rows.append({
                    "id": _make_id(it["link"], category),
                    "title": it["title"],
                    "link": it["link"],
                    "summary": it["summary"],
                    "source_domain": domain,
                    "source_category": category,
                    "pub_date": pub,
                    "fetched_at": fetched_at,
                })

        try:
            new_count = db.insert_items(rows)
            items_inserted += new_count
            db.upsert_feed_status(url, "ok", error=None, items_count=len(raw_items))
            feeds_ok += 1
            log.info("ok: %s — %d items (+%d new rows)", url, len(raw_items), new_count)
        except Exception as e:
            log.exception("db insert failed for %s", url)
            db.upsert_feed_status(url, "error", error=f"db: {e}"[:500], items_count=0)
            feeds_error += 1

    log.info("refresh complete: %d ok, %d err, %d items inserted",
             feeds_ok, feeds_error, items_inserted)
    return {
        "feeds_ok": feeds_ok,
        "feeds_error": feeds_error,
        "items_inserted": items_inserted,
    }
