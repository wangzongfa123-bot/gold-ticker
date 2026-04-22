import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.database import SessionLocal
from app.services.gold_price import fetch_gold_price
from app.services.alert import check_alerts
from app.services.fund_nav import fetch_history_nav
from app.websocket_manager import manager
from app import crud

scheduler = AsyncIOScheduler()


async def fetch_and_broadcast():
    """Fetch gold price, save to DB, check alerts, broadcast via WebSocket."""
    price_data = await fetch_gold_price()
    if not price_data:
        return

    db = SessionLocal()
    try:
        record = crud.create_price_record(
            db,
            price_cny=price_data.price_cny,
            high=price_data.high,
            low=price_data.low,
            open=price_data.open,
            source=price_data.source,
        )

        stats = crud.get_price_stats_24h(db)

        price_msg = {
            "type": "price_update",
            "data": {
                "price_cny": price_data.price_cny,
                "change": stats.get("change", 0),
                "change_percent": stats.get("change_percent", 0),
                "high_24h": stats.get("high_24h"),
                "low_24h": stats.get("low_24h"),
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
        await manager.broadcast(price_msg)

        triggered = check_alerts(db, price_data.price_cny)
        for alert_info in triggered:
            await manager.broadcast({
                "type": "alert_triggered",
                "data": alert_info,
            })
            print(f"[Alert] Triggered: {alert_info['name']}")

        print(f"[Scheduler] Gold price: ¥{price_data.price_cny}/g (source: {price_data.source})")
    finally:
        db.close()


async def cleanup_job():
    """Remove old price records."""
    db = SessionLocal()
    try:
        crud.cleanup_old_prices(db, settings.DATA_RETENTION_DAYS)
        print("[Scheduler] Old price data cleaned up")
    finally:
        db.close()


async def fetch_fund_navs():
    """Fetch NAV data for all recommended funds."""
    db = SessionLocal()
    try:
        funds = crud.get_fund_list(db)
        for fund in funds:
            navs = await fetch_history_nav(fund.code, page=1, page_size=30)
            if navs:
                for n in navs:
                    crud.upsert_nav(
                        db, fund.code, n["nav_date"],
                        n["nav"], n.get("accumulated_nav"),
                        n.get("daily_return"),
                    )
                print(f"[Scheduler] Fund {fund.code} {fund.name}: {len(navs)} NAV records")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        fetch_and_broadcast,
        "interval",
        seconds=settings.FETCH_INTERVAL_SECONDS,
        id="fetch_gold_price",
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup_job,
        "cron",
        hour=3, minute=0,
        id="cleanup_old_data",
        replace_existing=True,
    )
    scheduler.add_job(
        fetch_fund_navs,
        "cron",
        hour=16, minute=30,
        id="fetch_fund_navs",
        replace_existing=True,
    )
    scheduler.start()
    # Run first fetch immediately
    asyncio.get_event_loop().create_task(fetch_and_broadcast())
    asyncio.get_event_loop().create_task(fetch_fund_navs())


def stop_scheduler():
    scheduler.shutdown(wait=False)
