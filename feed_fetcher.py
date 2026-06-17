"""
RSS/Atom feed fetching and normalization.

Design:
- Each feed is fetched once per refresh cycle (URLs are de-duped via
  feeds.unique_feed_urls). Items are then fanned out to every category the URL
  is tagged with, so a feed that lives in both finance_daily and fintech_banking
  produces two rows per article.
- Single broken feed must never break the refresh loop — every fetch is wrapped
  in try/except and the error is persisted to feed_status.
- All timestamps are normalized to ISO 8601 UTC.
"""

import hashlib
import logging
import re
import socket
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse, parse_qs

import feedparser
from dateutil import parser as dateparser

from feeds import unique_feed_urls, categories_for_url

log = logging.getLogger("feed_fetcher")

USER_AGENT = "ClaudeNewsAggregator/1.0 (+sslip.io)"

# Normal feed items get a 2000-char summary cap. YouTube items go up to 8000
# so we can fit the transcript head (podcasts are long, headline alone is
# useless for the digest agent).
SUMMARY_CAP_DEFAULT = 2000
SUMMARY_CAP_YOUTUBE = 8000

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _strip_html(text):
    if not text:
        return ""
    no_tags = _HTML_TAG_RE.sub(" ", text)
    return _WHITESPACE_RE.sub(" ", no_tags).strip()


def _extract_youtube_video_id(url):
    """Return the 11-char video id from any common YouTube URL, or None."""
    try:
        p = urlparse(url)
        host = p.netloc.lower()
        if host.endswith("youtu.be"):
            return p.path.lstrip("/") or None
        if "youtube.com" in host:
            if p.path == "/watch":
                v = parse_qs(p.query).get("v", [None])[0]
                return v
            for prefix in ("/embed/", "/shorts/", "/live/"):
                if p.path.startswith(prefix):
                    return p.path[len(prefix):].split("/", 1)[0]
    except Exception:
        pass
    return None


def _fetch_youtube_transcript(video_id):
    """
    Best-effort fetch of an auto-generated transcript. Tries Russian, Kazakh,
    English (in that order). Returns plain text or None. Imports lazily so the
    module loads even if the optional dep is missing.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except Exception as e:
        log.debug("youtube-transcript-api not installed: %s", e)
        return None
    for langs in (["ru"], ["kk"], ["en"], ["ru", "kk", "en"]):
        try:
            entries = YouTubeTranscriptApi.get_transcript(video_id, languages=langs)
            text = " ".join(e["text"] for e in entries if e.get("text"))
            text = _WHITESPACE_RE.sub(" ", text).strip()
            if text:
                return text
        except Exception:
            continue
    log.debug("no transcript available for %s", video_id)
    return None


def _to_utc_iso(value):
    """
    Best-effort parse of a feed date into ISO 8601 UTC.
    Accepts time.struct_time, datetime, RFC 822 string, ISO string.
    """
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
            # Some feeds wrap the date in whitespace, e.g.
            # "<pubDate> Tue, 16 Jun 2026 18:38:20 +0500 </pubDate>".
            s = value.strip()
            if not s:
                return None
            try:
                dt = parsedate_to_datetime(s)
            except (TypeError, ValueError):
                dt = dateparser.parse(s)
            if dt is None:
                return None
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
    except Exception as e:
        log.debug("date parse failed for %r: %s", value, e)
    return None


# Match a YYYY-MM-DD or YYYY/MM/DD path segment — many KZ/RU sites embed the
# publish date in the URL when the feed itself omits pubDate.
_URL_DATE_RE = re.compile(r"/(20\d{2})[-/](\d{1,2})[-/](\d{1,2})(?:/|$)")


def _date_from_url(url):
    """Pull a publication date out of the URL path, or None if not present."""
    if not url:
        return None
    m = _URL_DATE_RE.search(url)
    if not m:
        return None
    try:
        y, mo, d = (int(x) for x in m.groups())
        if not (1 <= mo <= 12 and 1 <= d <= 31):
            return None
        dt = datetime(y, mo, d, 12, 0, 0, tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
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

    is_youtube_feed = "youtube.com/feeds/videos.xml" in url

    items = []
    for entry in parsed.entries:
        link = (entry.get("link") or "").strip()
        title = (entry.get("title") or "").strip()
        if not link or not title:
            continue

        # Prefer published_parsed, then updated_parsed, then string forms.
        # Last resort: try to extract YYYY-MM-DD from the article URL.
        pub_date = (
            _to_utc_iso(entry.get("published_parsed"))
            or _to_utc_iso(entry.get("updated_parsed"))
            or _to_utc_iso(entry.get("published"))
            or _to_utc_iso(entry.get("updated"))
            or _date_from_url(link)
        )

        summary_raw = entry.get("summary") or entry.get("description") or ""
        if not summary_raw and entry.get("content"):
            try:
                summary_raw = entry["content"][0].get("value", "")
            except (IndexError, AttributeError):
                summary_raw = ""
        if is_youtube_feed and not summary_raw:
            md = entry.get("media_description") or entry.get("yt_description")
            if md:
                summary_raw = md
        summary = _strip_html(summary_raw)[:SUMMARY_CAP_DEFAULT]

        if is_youtube_feed:
            video_id = _extract_youtube_video_id(link)
            if video_id:
                transcript = _fetch_youtube_transcript(video_id)
                if transcript:
                    head = (summary + "\n\n").strip() if summary else ""
                    combined = f"{head}--- TRANSCRIPT ---\n{transcript}"
                    summary = combined[:SUMMARY_CAP_YOUTUBE]

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

