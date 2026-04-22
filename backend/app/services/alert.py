from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.models import PriceAlert
from app.crud import get_active_alerts, update_alert


def check_alerts(db: Session, price_cny: float) -> List[dict]:
    """Check all active alerts against current price (CNY/g)."""
    triggered = []
    alerts = get_active_alerts(db)

    for alert in alerts:
        is_triggered = False

        if alert.condition == "above" and price_cny >= alert.threshold:
            is_triggered = True
        elif alert.condition == "below" and price_cny <= alert.threshold:
            is_triggered = True

        if is_triggered:
            update_alert(db, alert.id, is_active=False, triggered_at=datetime.utcnow())
            triggered.append({
                "alert_id": alert.id,
                "name": alert.name,
                "condition": alert.condition,
                "threshold": alert.threshold,
                "current_price": price_cny,
                "triggered_at": datetime.utcnow().isoformat(),
            })

    return triggered
