"""
FastAPI entrypoint for the Claude News Aggregator.
"""

import logging
import os
import threading
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from db import DB
from feed_fetcher import refresh_all_feeds
from feeds import FEEDS
from scheduler import make_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("main")

db = DB()
scheduler = make_scheduler(db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("starting up — %d feed entries, %d unique URLs",
             len(FEEDS), len({f["url"] for f in FEEDS}))
    # One-shot migration: heal items whose pub_date was previously stamped
    # with fetched_at because the source feed lacked a real publication date.
    try:
        fixed = db.repair_pub_dates_from_link()
        if fixed:
            log.info("repaired %d item pub_dates from URL path", fixed)
    except Exception:
        log.exception("pub_date repair migration failed")
    scheduler.start()
    threading.Thread(target=_initial_refresh, daemon=True).start()
    yield
    log.info("shutting down")
    try:
        scheduler.shutdown(wait=False)
    except Exception:
        pass


def _initial_refresh():
    try:
        log.info("running initial refresh")
        refresh_all_feeds(db)
    except Exception:
        log.exception("initial refresh failed")


app = FastAPI(title="Claude News Aggregator", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _expected_key():
    key = os.environ.get("NEWS_API_KEY", "")
    if not key:
        raise HTTPException(status_code=503, detail="API key not configured")
    return key


def _extract_token(authorization, key):
    if authorization and authorization.startswith("Bearer "):
        return authorization.removeprefix("Bearer ").strip()
    if key:
        return key.strip()
    return None


def require_auth(
    authorization: Optional[str] = Header(None),
    key: Optional[str] = Query(None, description="API key as query param (for clients that can't set headers, e.g. WebFetch)"),
) -> bool:
    expected = _expected_key()
    token = _extract_token(authorization, key)
    if not token:
        raise HTTPException(status_code=401, detail="missing api key (Bearer header or ?key=)")
    if token != expected:
        raise HTTPException(status_code=401, detail="invalid token")
    return True


def optional_auth(
    authorization: Optional[str] = Header(None),
    key: Optional[str] = Query(None),
) -> bool:
    try:
        expected = os.environ.get("NEWS_API_KEY", "")
        if not expected:
            return False
        token = _extract_token(authorization, key)
        return bool(token) and token == expected
    except Exception:
        return False


@app.get("/health")
def health(authed: bool = Depends(optional_auth)):
    base = {"status": "ok"}
    if not authed:
        return base
    return {
        "status": "ok",
        "db_items_count": db.count_items(),
        "last_refresh": db.last_refresh(),
        "sources_count": len({f["url"] for f in FEEDS}),
    }


@app.get("/news")
def news(
    _auth: bool = Depends(require_auth),
    category: Optional[str] = Query(None),
    hours_back: int = Query(48, ge=1, le=24 * 30),
    source: Optional[str] = Query(None, description="source_domain exact match"),
    query: Optional[str] = Query(None, description="case-insensitive substring in title or summary"),
    limit: int = Query(30, ge=1, le=500),
):
    items = db.get_items(
        category=category,
        hours_back=hours_back,
        source=source,
        query=query,
        limit=limit,
    )
    return items


@app.get("/sources")
def sources(_auth: bool = Depends(require_auth)):
    return db.get_sources_status()


@app.post("/refresh")
def refresh(_auth: bool = Depends(require_auth)):
    summary = refresh_all_feeds(db)
    return {"status": "ok", **summary}
