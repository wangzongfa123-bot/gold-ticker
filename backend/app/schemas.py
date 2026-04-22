from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


# --- Gold Price Schemas ---

class GoldPriceBase(BaseModel):
    price_cny: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    source: str = "unknown"


class GoldPriceOut(GoldPriceBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class GoldPriceCurrentOut(BaseModel):
    price_cny: float
    change: Optional[float] = None
    change_percent: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    timestamp: datetime


class KlineItem(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float


class PriceStatsOut(BaseModel):
    current: float
    open_24h: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None


# --- Alert Schemas ---

class AlertCreate(BaseModel):
    name: str
    condition: str  # "above" or "below"
    threshold: float


class AlertUpdate(BaseModel):
    name: Optional[str] = None
    condition: Optional[str] = None
    threshold: Optional[float] = None
    is_active: Optional[bool] = None


class AlertOut(BaseModel):
    id: int
    name: str
    condition: str
    threshold: float
    is_active: bool
    triggered_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- WebSocket Message Schemas ---

class WSPriceUpdate(BaseModel):
    type: str = "price_update"
    data: GoldPriceCurrentOut


class WSAlertTriggered(BaseModel):
    type: str = "alert_triggered"
    data: dict


# --- Forecast & Quant Schemas ---

class ForecastPoint(BaseModel):
    timestamp: str
    predicted: float
    upper: float
    lower: float


class ForecastOut(BaseModel):
    forecast: List[ForecastPoint]
    confidence: str
    trend: str
    trend_strength: float
    current_price: float
    mom_short_avg: float
    mom_long_avg: float
    residual_std: float


class QuantMA(BaseModel):
    ma5: Optional[float] = None
    ma10: Optional[float] = None
    ma20: Optional[float] = None


class QuantBB(BaseModel):
    upper: Optional[float] = None
    middle: Optional[float] = None
    lower: Optional[float] = None
    width: Optional[float] = None
    position: Optional[float] = None


class QuantMACD(BaseModel):
    macd: Optional[float] = None
    dif: Optional[float] = None
    dea: Optional[float] = None
    histogram: List[float] = []


class QuantVolatility(BaseModel):
    interval: float
    daily: float
    annualized: float


class QuantMomentum(BaseModel):
    mom_5: Optional[float] = None
    mom_10: Optional[float] = None
    mom_20: Optional[float] = None


class QuantSignal(BaseModel):
    indicator: str
    signal: str
    strength: str


class QuantOut(BaseModel):
    current_price: float
    ma: QuantMA
    bollinger: QuantBB
    rsi: Optional[float] = None
    macd: QuantMACD
    volatility: QuantVolatility
    momentum: QuantMomentum
    signals: List[QuantSignal]


# --- Fund Schemas ---

class FundInfoOut(BaseModel):
    code: str
    name: str
    category: str
    reason: str = ""

    class Config:
        from_attributes = True


class FundNavOut(BaseModel):
    nav_date: str
    nav: float
    accumulated_nav: Optional[float] = None
    daily_return: Optional[float] = None


class FundNavHistoryOut(BaseModel):
    code: str
    name: str
    navs: List[FundNavOut]


class FundAnalysisOut(BaseModel):
    code: str
    name: str
    category: str
    current_nav: Optional[float] = None
    daily_return: Optional[float] = None
    momentum_5d: Optional[float] = None
    momentum_20d: Optional[float] = None
    recommendation_reason: str = ""
    lot_size: int = 100
    lot_price: Optional[float] = None
