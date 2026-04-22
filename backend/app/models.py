from datetime import datetime

from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Enum
import enum

from app.database import Base


class GoldPrice(Base):
    __tablename__ = "gold_prices"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    price_cny = Column(Float, nullable=False)  # CNY/克
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    source = Column(String, default="unknown")


class AlertCondition(str, enum.Enum):
    ABOVE = "above"
    BELOW = "below"


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    condition = Column(String, nullable=False)  # "above" or "below"
    threshold = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class FundInfo(Base):
    __tablename__ = "fund_infos"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(20), nullable=False)  # "gold", "a_share", "overseas"
    reason = Column(String(500), nullable=True)  # auto-generated recommendation reason
    source_url = Column(String(255), nullable=True)
    fetch_method = Column(String(20), default="eastmoney_nav")
    created_at = Column(DateTime, default=datetime.utcnow)


class FundNav(Base):
    __tablename__ = "fund_navs"

    id = Column(Integer, primary_key=True, index=True)
    fund_code = Column(String(10), nullable=False, index=True)
    nav_date = Column(String(10), nullable=False)  # "2024-01-15"
    nav = Column(Float, nullable=False)
    accumulated_nav = Column(Float, nullable=True)
    daily_return = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
