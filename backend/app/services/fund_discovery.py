import re

import httpx


# Keywords to identify gold-related funds
GOLD_KEYWORDS = ["黄金", "金ETF", "Au9999", "黄金ETF"]


def _parse_rank_response(text: str) -> list[dict]:
    """Parse eastmoney rankhandler JSONP response."""
    match = re.search(r"rankData\s*=\s*(\{.*?\})\s*$", text, re.DOTALL)
    if not match:
        return []
    import json
    data = json.loads(match.group(1))
    if data.get("ErrCode") != 0 and data.get("ErrCode") is not None:
        return []
    raw_list = data.get("datas", [])
    funds = []
    for raw in raw_list:
        parts = raw.split(",")
        if len(parts) < 10:
            continue
        funds.append({
            "code": parts[0],
            "name": parts[1],
            "nav_date": parts[3],
            "nav": float(parts[4]) if parts[4] else 0,
            "accumulated_nav": float(parts[5]) if parts[5] else 0,
            "daily_return": float(parts[6]) if parts[6] else 0,
            "return_1w": float(parts[7]) if parts[7] else 0,
            "return_1m": float(parts[8]) if parts[8] else 0,
            "return_3m": float(parts[9]) if parts[9] else 0,
            "return_6m": float(parts[10]) if len(parts) > 10 and parts[10] else 0,
            "return_1y": float(parts[11]) if len(parts) > 11 and parts[11] else 0,
        })
    return funds


_HEADERS = {
    "Referer": "https://fund.eastmoney.com/rank.html",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}


def _build_params(fund_type: str, page: int = 1, size: int = 50) -> dict:
    return {
        "op": "ph", "dt": "kf", "ft": fund_type,
        "rs": "", "gs": 0, "sc": "j6yzf", "st": "desc",
        "sd": "2025-10-17", "ed": "2026-04-17", "qdii": "",
        "tabSubtype": "101,102,103,104,105,",
        "f": "", "fc": "", "pi": page, "pn": size,
    }


async def fetch_popular_funds() -> list[dict]:
    """Fetch popular A-share funds (混合型 + 股票型) from eastmoney."""
    funds = []
    async with httpx.AsyncClient(timeout=15) as client:
        for ft in ("hh", "gp"):
            resp = await client.get(
                "http://fund.eastmoney.com/data/rankhandler.aspx",
                params=_build_params(ft, size=50),
                headers=_HEADERS,
            )
            funds.extend(_parse_rank_response(resp.text))
    return funds


async def fetch_qdii_funds() -> list[dict]:
    """Fetch QDII/overseas funds from eastmoney."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "http://fund.eastmoney.com/data/rankhandler.aspx",
            params=_build_params("qdii", size=50),
            headers=_HEADERS,
        )
        return _parse_rank_response(resp.text)


def is_gold_fund(name: str) -> bool:
    """Check if a fund name indicates gold-related."""
    return any(kw in name for kw in GOLD_KEYWORDS)


def generate_reason(fund: dict, category: str) -> str:
    """Auto-generate recommendation reason based on fund data."""
    r6m = fund.get("return_6m", 0)
    r1y = fund.get("return_1y", 0)
    daily = fund.get("daily_return", 0)

    if category == "gold":
        return f"黄金主题基金，近6月涨幅{r6m:.1f}%，抗通胀避险资产配置首选"
    elif category == "overseas":
        return f"QDII海外基金，近6月涨幅{r6m:.1f}%，分散A股风险全球化配置"
    else:
        if r6m > 30:
            return f"近6月涨幅{r6m:.1f}%，近1年{r1y:.1f}%，业绩突出成长性强"
        elif daily < -1:
            return f"近期回调{abs(daily):.1f}%，估值低位布局良机"
        else:
            return f"近6月涨幅{r6m:.1f}%，业绩稳健配置价值突出"
