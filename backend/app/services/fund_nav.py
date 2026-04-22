import re
from typing import Optional

import httpx


async def fetch_realtime_nav(code: str) -> Optional[dict]:
    """Fetch real-time estimated NAV from eastmoney (fundgz.1234567.com.cn).

    Returns dict with fields: name, gztime, dwjz (previous NAV),
    gsz (estimated NAV), gszzl (change %).
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"http://fundgz.1234567.com.cn/js/{code}.js"
            )
            resp.raise_for_status()
            # Response format: jsonpgz({...});
            match = re.search(r"jsonpgz\((.*?)\);", resp.text)
            if not match:
                return None
            import json
            data = json.loads(match.group(1))
            return {
                "name": data.get("name", ""),
                "gztime": data.get("gztime", ""),
                "dwjz": float(data.get("dwjz", 0)),
                "gsz": float(data.get("gsz", 0)),
                "gszzl": float(data.get("gszzl", 0)),
            }
    except Exception as e:
        print(f"[FundNav] Realtime fetch error for {code}: {e}")
        return None


async def fetch_history_nav(code: str, page: int = 1, page_size: int = 30) -> Optional[list]:
    """Fetch historical NAV from eastmoney API.

    Returns list of dicts with fields: nav_date, nav, accumulated_nav, daily_return.
    """
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "http://api.fund.eastmoney.com/f10/lsjz",
                params={
                    "fundCode": code,
                    "pageIndex": page,
                    "pageSize": page_size,
                },
                headers={
                    "Referer": "https://fundf10.eastmoney.com/",
                },
            )
            resp.raise_for_status()
            result = resp.json()
            if result.get("ErrCode") != 0 or not result.get("Data"):
                return []

            lsjz_list = result["Data"].get("LSJZList", [])
            navs = []
            for item in lsjz_list:
                navs.append({
                    "nav_date": item.get("FSRQ", ""),
                    "nav": float(item.get("DWJZ", 0)),
                    "accumulated_nav": float(item.get("LJJZ", 0)) or None,
                    "daily_return": float(item.get("JZZZL", 0)),
                })
            return navs
    except Exception as e:
        print(f"[FundNav] History fetch error for {code}: {e}")
        return None
