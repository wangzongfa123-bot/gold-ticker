import math
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.models import GoldPrice, PriceAlert, FundInfo, FundNav


# --- Gold Price CRUD ---

def create_price_record(db: Session, price_cny: float,
                        open: Optional[float] = None,
                        high: Optional[float] = None,
                        low: Optional[float] = None,
                        source: str = "unknown") -> GoldPrice:
    record = GoldPrice(
        price_cny=price_cny,
        open=open or price_cny,
        high=high or price_cny,
        low=low or price_cny,
        close=price_cny,
        source=source,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_latest_price(db: Session) -> Optional[GoldPrice]:
    return db.query(GoldPrice).order_by(desc(GoldPrice.timestamp)).first()


def get_price_history(db: Session, limit: int = 100,
                      start: Optional[datetime] = None,
                      end: Optional[datetime] = None) -> List[GoldPrice]:
    query = db.query(GoldPrice)
    if start:
        query = query.filter(GoldPrice.timestamp >= start)
    if end:
        query = query.filter(GoldPrice.timestamp <= end)
    return query.order_by(desc(GoldPrice.timestamp)).limit(limit).all()


def get_price_stats_24h(db: Session) -> dict:
    since = datetime.utcnow() - timedelta(hours=24)
    records = db.query(GoldPrice).filter(GoldPrice.timestamp >= since).all()
    if not records:
        return {}
    prices = [r.price_cny for r in records]
    oldest = min(records, key=lambda r: r.timestamp)
    latest = max(records, key=lambda r: r.timestamp)
    change = latest.price_cny - oldest.price_cny
    change_pct = (change / oldest.price_cny * 100) if oldest.price_cny else 0
    return {
        "current": latest.price_cny,
        "open_24h": oldest.price_cny,
        "high_24h": max(prices),
        "low_24h": min(prices),
        "change": round(change, 2),
        "change_percent": round(change_pct, 4),
        "timestamp": latest.timestamp,
    }


def get_kline_data(db: Session, interval_minutes: int = 60, limit: int = 100) -> List[dict]:
    since = datetime.utcnow() - timedelta(minutes=interval_minutes * limit)
    records = db.query(GoldPrice).filter(
        GoldPrice.timestamp >= since
    ).order_by(GoldPrice.timestamp).all()

    if not records:
        return []

    buckets = {}
    for r in records:
        bucket_ts = r.timestamp.replace(
            minute=(r.timestamp.minute // interval_minutes) * interval_minutes if interval_minutes < 60
            else 0,
            second=0, microsecond=0
        )
        if interval_minutes >= 60:
            hour_bucket = (r.timestamp.hour // (interval_minutes // 60)) * (interval_minutes // 60)
            bucket_ts = bucket_ts.replace(hour=hour_bucket)

        key = bucket_ts.isoformat()
        if key not in buckets:
            buckets[key] = {"timestamp": bucket_ts.isoformat() + "Z", "open": r.price_cny, "high": r.price_cny,
                            "low": r.price_cny, "close": r.price_cny}
        else:
            buckets[key]["high"] = max(buckets[key]["high"], r.price_cny)
            buckets[key]["low"] = min(buckets[key]["low"], r.price_cny)
            buckets[key]["close"] = r.price_cny

    result = sorted(buckets.values(), key=lambda x: x["timestamp"])  # ISO string sorts correctly
    return result[-limit:]


def cleanup_old_prices(db: Session, retention_days: int = 90):
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    db.query(GoldPrice).filter(GoldPrice.timestamp < cutoff).delete()
    db.commit()


# --- Alert CRUD ---

def create_alert(db: Session, name: str, condition: str, threshold: float) -> PriceAlert:
    alert = PriceAlert(name=name, condition=condition, threshold=threshold)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alerts(db: Session) -> List[PriceAlert]:
    return db.query(PriceAlert).order_by(desc(PriceAlert.created_at)).all()


def get_active_alerts(db: Session) -> List[PriceAlert]:
    return db.query(PriceAlert).filter(PriceAlert.is_active == True).all()


def get_alert(db: Session, alert_id: int) -> Optional[PriceAlert]:
    return db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()


def update_alert(db: Session, alert_id: int, **kwargs) -> Optional[PriceAlert]:
    alert = get_alert(db, alert_id)
    if not alert:
        return None
    for key, value in kwargs.items():
        if value is not None:
            setattr(alert, key, value)
    db.commit()
    db.refresh(alert)
    return alert


def delete_alert(db: Session, alert_id: int) -> bool:
    alert = get_alert(db, alert_id)
    if not alert:
        return False
    db.delete(alert)
    db.commit()
    return True


# --- Forecast & Quantitative Analysis ---

def get_price_forecast(db: Session, hours: int = 48) -> dict:
    """Predict gold prices for the next N hours using linear regression + momentum.

    Uses the last 100 price points to fit a linear trend,
    then adjusts with short-term momentum and mean-reversion.
    """
    records = (
        db.query(GoldPrice)
        .order_by(desc(GoldPrice.timestamp))
        .limit(100)
        .all()
    )
    if len(records) < 10:
        return {"forecast": [], "confidence": "low", "trend": "unknown", "trend_strength": 0}

    records.reverse()  # oldest first
    closes = [r.price_cny for r in records]
    timestamps = [r.timestamp for r in records]

    # Linear regression: y = a + b*x
    n = len(closes)
    x_vals = list(range(n))
    x_mean = sum(x_vals) / n
    y_mean = sum(closes) / n
    b = sum((x_vals[i] - x_mean) * (closes[i] - y_mean) for i in range(n)) / sum(
        (x_vals[i] - x_mean) ** 2 for i in range(n)
    )
    a = y_mean - b * x_mean

    # Calculate residual std for confidence bands
    residuals = [closes[i] - (a + b * x_vals[i]) for i in range(n)]
    std_resid = (sum(r ** 2 for r in residuals) / (n - 2)) ** 0.5

    # Momentum: compare last 5 vs last 20 avg
    mom_short = sum(closes[-5:]) / 5
    mom_long = sum(closes[-20:]) / 20
    momentum = mom_short - mom_long

    # Mean-reversion factor
    latest = closes[-1]
    mean_reversion = (y_mean - latest) * 0.1

    # Average interval between records for projecting timestamps
    if len(timestamps) >= 2:
        avg_interval = (timestamps[-1] - timestamps[0]).total_seconds() / (n - 1)
    else:
        avg_interval = 300  # 5 minutes default

    last_ts = timestamps[-1]
    forecast_points = []
    steps_in_interval = hours * 3600 / avg_interval if avg_interval else 1
    total_steps = n + int(steps_in_interval)

    for step in range(n, min(n + int(steps_in_interval), n + 200)):
        base = a + b * step
        # Blend linear trend with momentum, fading momentum over time
        fade = max(0, 1 - (step - n) / steps_in_interval) if steps_in_interval else 0
        adjustment = momentum * fade * 0.3 + mean_reversion * fade * 0.2
        predicted = base + adjustment
        ts = last_ts + timedelta(seconds=avg_interval * (step - n + 1))

        # Confidence widens with distance
        width = std_resid * (1 + (step - n) / steps_in_interval * 2) if steps_in_interval else std_resid

        forecast_points.append({
            "timestamp": ts.isoformat() + "Z",
            "predicted": round(predicted, 2),
            "upper": round(predicted + width, 2),
            "lower": round(predicted - width, 2),
        })

    # Overall trend assessment
    trend_slope = b * n / latest if latest else 0
    if trend_slope > 0.002:
        trend = "up"
    elif trend_slope < -0.002:
        trend = "down"
    else:
        trend = "flat"

    trend_strength = round(abs(trend_slope) * 1000, 2)

    return {
        "forecast": forecast_points,
        "confidence": "high" if std_resid < latest * 0.005 else ("medium" if std_resid < latest * 0.01 else "low"),
        "trend": trend,
        "trend_strength": trend_strength,
        "current_price": latest,
        "mom_short_avg": round(mom_short, 2),
        "mom_long_avg": round(mom_long, 2),
        "residual_std": round(std_resid, 2),
    }


def get_quant_analysis(db: Session) -> dict:
    """Compute quantitative indicators from historical price data.

    Returns: RSI(14), MACD, MA(5/10/20), Bollinger Bands, volatility, momentum.
    """
    records = (
        db.query(GoldPrice)
        .order_by(desc(GoldPrice.timestamp))
        .limit(200)
        .all()
    )
    if len(records) < 20:
        return {"error": "insufficient data"}

    records.reverse()
    closes = [r.price_cny for r in records]
    n = len(closes)
    latest = closes[-1]

    # --- Moving Averages ---
    def ma(period):
        if n < period:
            return None
        return round(sum(closes[-period:]) / period, 2)

    ma5 = ma(5)
    ma10 = ma(10)
    ma20 = ma(20)

    # --- Bollinger Bands (20-period, 2 std) ---
    if ma20 is not None:
        std_20 = (sum((closes[-20 - i] - ma20) ** 2 for i in range(20)) / 20) ** 0.5
        bb_upper = round(ma20 + 2 * std_20, 2)
        bb_lower = round(ma20 - 2 * std_20, 2)
        bb_width = round((bb_upper - bb_lower) / ma20 * 100, 4) if ma20 else 0
    else:
        bb_upper = bb_lower = bb_width = None

    # --- RSI (14-period) ---
    if n >= 15:
        deltas = [closes[i] - closes[i - 1] for i in range(n - 1)]
        recent_14 = deltas[-14:]
        gains = [d for d in recent_14 if d > 0]
        losses = [-d for d in recent_14 if d < 0]
        avg_gain = sum(gains) / 14 if gains else 0
        avg_loss = sum(losses) / 14 if losses else 0
        if avg_gain == 0 and avg_loss == 0:
            rsi = 50.0  # neutral when no movement
        elif avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = round(100 - 100 / (1 + rs), 2)
    else:
        rsi = None

    # --- MACD (12, 26, 9 simplified) ---
    if n >= 26:
        def ema(data, period):
            k = 2 / (period + 1)
            result = [data[0]]
            for val in data[1:]:
                result.append(val * k + result[-1] * (1 - k))
            return result

        ema12 = ema(closes, 12)
        ema26 = ema(closes, 26)
        dif = [ema12[i] - ema26[i] for i in range(len(ema26))]
        dea = ema(dif, 9)
        macd_line = [2 * (dif[-1 - i] - dea[-1 - i]) for i in range(min(9, len(dif)))]
        macd_line.reverse()
        macd_val = round(macd_line[-1] if macd_line else 0, 4)
        dif_val = round(dif[-1], 4)
        dea_val = round(dea[-1], 4)
    else:
        macd_val = dif_val = dea_val = None
        macd_line = []

    # --- Volatility (annualized, from recent returns) ---
    if n >= 2:
        returns = [(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, n)]
        recent_returns = returns[-30:]  # last 30 intervals
        mean_ret = sum(recent_returns) / len(recent_returns)
        variance = sum((r - mean_ret) ** 2 for r in recent_returns) / len(recent_returns)
        interval_vol = variance ** 0.5
        # Annualize assuming 5-min intervals, ~24*12 = 288 per day, ~250 trading days
        annualized_vol = round(interval_vol * (288 * 250) ** 0.5 * 100, 4)
        daily_vol = round(interval_vol * 288 ** 0.5 * 100, 4)
    else:
        interval_vol = annualized_vol = daily_vol = 0

    # --- Momentum ---
    mom_5 = round(closes[-1] - closes[-5], 4) if n >= 5 else None
    mom_10 = round(closes[-1] - closes[-10], 4) if n >= 10 else None
    mom_20 = round(closes[-1] - closes[-20], 4) if n >= 20 else None

    # --- Price position relative to BB ---
    if bb_upper and bb_lower and (bb_upper - bb_lower) > 0.01:
        bb_position = round((latest - bb_lower) / (bb_upper - bb_lower) * 100, 2)
    else:
        bb_position = None

    # --- Signal synthesis ---
    signals = []
    # MA alignment
    if ma5 and ma10 and ma20:
        if ma5 > ma10 > ma20:
            signals.append({"indicator": "均线排列", "signal": "多头", "strength": "strong"})
        elif ma5 < ma10 < ma20:
            signals.append({"indicator": "均线排列", "signal": "空头", "strength": "strong"})
        else:
            signals.append({"indicator": "均线排列", "signal": "震荡", "strength": "weak"})

    # RSI
    if rsi is not None:
        if rsi > 70:
            signals.append({"indicator": "RSI", "signal": "超买", "strength": "warning"})
        elif rsi < 30:
            signals.append({"indicator": "RSI", "signal": "超卖", "strength": "warning"})
        else:
            signals.append({"indicator": "RSI", "signal": "中性", "strength": "neutral"})

    # MACD
    if macd_val is not None and dif_val is not None and dea_val is not None:
        if dif_val > dea_val and macd_val > 0:
            signals.append({"indicator": "MACD", "signal": "金叉向上", "strength": "strong"})
        elif dif_val < dea_val and macd_val < 0:
            signals.append({"indicator": "MACD", "signal": "死叉向下", "strength": "strong"})
        else:
            signals.append({"indicator": "MACD", "signal": "震荡", "strength": "weak"})

    # BB position
    if bb_position is not None:
        if bb_position > 80:
            signals.append({"indicator": "布林带", "signal": "接近上轨（压力）", "strength": "warning"})
        elif bb_position < 20:
            signals.append({"indicator": "布林带", "signal": "接近下轨（支撑）", "strength": "warning"})
        else:
            signals.append({"indicator": "布林带", "signal": "区间内", "strength": "neutral"})

    return {
        "current_price": latest,
        "ma": {"ma5": ma5, "ma10": ma10, "ma20": ma20},
        "bollinger": {
            "upper": bb_upper,
            "middle": ma20,
            "lower": bb_lower,
            "width": bb_width,
            "position": bb_position,
        },
        "rsi": rsi,
        "macd": {
            "macd": macd_val,
            "dif": dif_val,
            "dea": dea_val,
            "histogram": macd_line,
        },
        "volatility": {
            "interval": round(interval_vol * 100, 4),
            "daily": daily_vol,
            "annualized": annualized_vol,
        },
        "momentum": {
            "mom_5": mom_5,
            "mom_10": mom_10,
            "mom_20": mom_20,
        },
        "signals": signals,
    }


# --- Fund CRUD ---

def seed_fund_info(db: Session, funds: List[dict]) -> int:
    """Insert fund list, skip existing codes."""
    count = 0
    for f in funds:
        existing = db.query(FundInfo).filter(FundInfo.code == f["code"]).first()
        if existing:
            continue
        record = FundInfo(
            code=f["code"],
            name=f["name"],
            category=f["category"],
            reason=f.get("reason"),
            source_url=f.get("source_url"),
            fetch_method=f.get("fetch_method", "eastmoney_nav"),
        )
        db.add(record)
        count += 1
    if count:
        db.commit()
    return count


def update_fund_reason(db: Session, code: str, reason: str):
    """Update recommendation reason for a fund."""
    fund = db.query(FundInfo).filter(FundInfo.code == code).first()
    if fund:
        fund.reason = reason
        db.commit()


def get_fund_list(db: Session, category: Optional[str] = None) -> List[FundInfo]:
    query = db.query(FundInfo)
    if category:
        query = query.filter(FundInfo.category == category)
    return query.order_by(FundInfo.id).all()


def get_fund_by_code(db: Session, code: str) -> Optional[FundInfo]:
    return db.query(FundInfo).filter(FundInfo.code == code).first()


def upsert_nav(db: Session, fund_code: str, nav_date: str, nav: float,
               accumulated_nav: Optional[float] = None,
               daily_return: Optional[float] = None) -> FundNav:
    """Insert NAV record if not exists, skip duplicate dates."""
    existing = db.query(FundNav).filter(
        FundNav.fund_code == fund_code,
        FundNav.nav_date == nav_date,
    ).first()
    if existing:
        return existing
    record = FundNav(
        fund_code=fund_code,
        nav_date=nav_date,
        nav=nav,
        accumulated_nav=accumulated_nav,
        daily_return=daily_return,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_nav_history(db: Session, fund_code: str, limit: int = 30) -> List[FundNav]:
    return (
        db.query(FundNav)
        .filter(FundNav.fund_code == fund_code)
        .order_by(desc(FundNav.nav_date))
        .limit(limit)
        .all()
    )


def cleanup_old_navs(db: Session, retention_days: int = 90):
    cutoff = (datetime.utcnow() - timedelta(days=retention_days)).strftime("%Y-%m-%d")
    db.query(FundNav).filter(FundNav.nav_date < cutoff).delete()
    db.commit()
