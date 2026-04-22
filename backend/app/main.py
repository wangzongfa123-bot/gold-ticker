import random
import math
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import GoldPrice
from app.scheduler import start_scheduler, stop_scheduler
from app.routers import prices, alerts, ws, funds


async def seed_historical_data():
    """Generate simulated historical data with realistic price variance."""
    from app.services.gold_price import fetch_gold_price

    db = SessionLocal()
    try:
        if db.query(GoldPrice).first() is not None:
            return

        # Fetch real price as baseline
        real = await fetch_gold_price()
        base_price = real.price_cny if real else 1000.0

        now = datetime.utcnow()
        price = base_price
        random.seed()  # use current time as seed for variety
        total_points = 864
        for i in range(total_points):
            ts = now - timedelta(minutes=5 * (total_points - i))
            # Mean-reverting random walk with cyclical trend
            mean_rev = (base_price - price) * 0.02
            momentum = random.gauss(0, 1.2)
            trend = 0.05 * math.sin(i / 30)
            change = momentum + mean_rev + trend
            price = price + change
            price = max(min(price, base_price * 1.02), base_price * 0.98)
            open_p = price + random.uniform(-1, 1)
            high = max(price, open_p) + random.uniform(0.2, 2.0)
            low = min(price, open_p) - random.uniform(0.2, 2.0)
            record = GoldPrice(
                timestamp=ts,
                price_cny=round(price, 2),
                open=round(open_p, 2),
                high=round(high, 2),
                low=round(low, 2),
                close=round(price, 2),
                source="simulated",
            )
            db.add(record)
        db.commit()
        print(f"[Seed] Generated {total_points} records based on ¥{base_price:.2f}/g")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    await seed_historical_data()
    from app.seed_funds import seed_funds
    seed_funds()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Gold Monitor API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prices.router)
app.include_router(alerts.router)
app.include_router(ws.router)
app.include_router(funds.router)


@app.get("/")
def root():
    return {"message": "Gold Monitor API", "docs": "/docs"}
