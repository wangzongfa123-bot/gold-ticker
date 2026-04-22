import httpx
from typing import Optional
from dataclasses import dataclass


@dataclass
class GoldPriceData:
    price_cny: float
    high: Optional[float] = None
    low: Optional[float] = None
    open: Optional[float] = None
    pre_close: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    source: str = "unknown"


async def fetch_from_cmb() -> Optional[GoldPriceData]:
    """Fetch gold price from 招商银行 (China Merchants Bank) API — Au99.99."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://m.cmbchina.com/api/rate/gold")
            resp.raise_for_status()
            result = resp.json()
            if result.get("returnCode") != "SUC0000":
                print(f"[CMB] API error: {result.get('errorMsg')}")
                return None

            items = result.get("body", {}).get("data", [])
            # Find Au99.99 (黄金现货)
            target = None
            for item in items:
                if item.get("goldNo") == "AU9999":
                    target = item
                    break
            if not target:
                print("[CMB] Au99.99 not found in response")
                return None

            cur_price = float(target["curPrice"])
            if cur_price <= 0:
                print("[CMB] Au99.99 price is 0 (market may be closed)")
                return None

            up_down = float(target.get("upDown", 0))
            pre_close = float(target.get("preClose", 0))
            change_pct = round(up_down / pre_close * 100, 4) if pre_close else 0

            return GoldPriceData(
                price_cny=cur_price,
                high=float(target.get("high", 0)) or None,
                low=float(target.get("low", 0)) or None,
                open=float(target.get("open", 0)) or None,
                pre_close=pre_close or None,
                change=up_down,
                change_percent=change_pct,
                source="招商银行",
            )
    except Exception as e:
        print(f"[CMB] Error: {e}")
        return None


async def fetch_gold_price() -> Optional[GoldPriceData]:
    """Fetch gold price from CMB."""
    result = await fetch_from_cmb()
    if result:
        return result
    print("[GoldPrice] Failed to fetch from CMB")
    return None
