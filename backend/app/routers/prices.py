from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/api/prices", tags=["prices"])


@router.get("/current", response_model=schemas.GoldPriceCurrentOut)
def get_current_price(db: Session = Depends(get_db)):
    stats = crud.get_price_stats_24h(db)
    if not stats:
        latest = crud.get_latest_price(db)
        if not latest:
            return schemas.GoldPriceCurrentOut(
                price_cny=0, timestamp=datetime.utcnow()
            )
        return schemas.GoldPriceCurrentOut(
            price_cny=latest.price_cny,
            timestamp=latest.timestamp,
        )
    return schemas.GoldPriceCurrentOut(
        price_cny=stats["current"],
        change=stats.get("change"),
        change_percent=stats.get("change_percent"),
        high_24h=stats.get("high_24h"),
        low_24h=stats.get("low_24h"),
        timestamp=stats.get("timestamp", datetime.utcnow()),
    )


@router.get("/history")
def get_price_history(
    limit: int = Query(100, le=500),
    start: Optional[str] = None,
    end: Optional[str] = None,
    db: Session = Depends(get_db),
):
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None
    records = crud.get_price_history(db, limit=limit, start=start_dt, end=end_dt)
    return [schemas.GoldPriceOut.model_validate(r) for r in records]


INTERVAL_MAP = {
    "5m": 5,
    "15m": 15,
    "1h": 60,
    "4h": 240,
    "1d": 1440,
}


@router.get("/kline")
def get_kline(
    interval: str = Query("1h", pattern="^(5m|15m|1h|4h|1d)$"),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    minutes = INTERVAL_MAP.get(interval, 60)
    data = crud.get_kline_data(db, interval_minutes=minutes, limit=limit)
    return data


@router.get("/stats", response_model=schemas.PriceStatsOut)
def get_stats(db: Session = Depends(get_db)):
    stats = crud.get_price_stats_24h(db)
    if not stats:
        return schemas.PriceStatsOut(current=0)
    return schemas.PriceStatsOut(
        current=stats["current"],
        open_24h=stats.get("open_24h"),
        high_24h=stats.get("high_24h"),
        low_24h=stats.get("low_24h"),
        change=stats.get("change"),
        change_percent=stats.get("change_percent"),
    )


@router.get("/forecast", response_model=schemas.ForecastOut)
def get_forecast(
    hours: int = Query(48, le=168),
    db: Session = Depends(get_db),
):
    return crud.get_price_forecast(db, hours=hours)


@router.get("/quant", response_model=schemas.QuantOut)
def get_quant_analysis(db: Session = Depends(get_db)):
    return crud.get_quant_analysis(db)
