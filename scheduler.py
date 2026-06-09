"""
APScheduler wiring.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.interval import IntervalTrigger

from feed_fetcher import refresh_all_feeds

log = logging.getLogger("scheduler")

REFRESH_MINUTES = 20


def make_scheduler(db):
    sched = BackgroundScheduler(
        executors={"default": ThreadPoolExecutor(max_workers=1)},
        job_defaults={
            "coalesce": True,
            "max_instances": 1,
            "misfire_grace_time": 60 * 5,
        },
        timezone="UTC",
    )

    def _job():
        try:
            refresh_all_feeds(db)
        except Exception:
            log.exception("scheduled refresh failed")

    sched.add_job(
        _job,
        trigger=IntervalTrigger(minutes=REFRESH_MINUTES),
        id="refresh_all_feeds",
        replace_existing=True,
    )
    return sched
