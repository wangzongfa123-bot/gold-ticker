from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/api/funds", tags=["funds"])

RECOMMENDATION_REASONS = {
    "518880": "黄金ETF龙头，流动性好，跟踪国内金价，抗通胀避险首选",
    "159937": "博时旗下黄金ETF，费率低，规模适中，配置价值突出",
    "005827": "张坤管理，重仓消费白马，长期业绩优秀，适合价值投资",
    "260108": "刘彦春管理，消费+医药双主线，穿越牛熊能力强",
    "003095": "葛兰管理，医药赛道龙头，集采风险出清后弹性大",
    "161725": "招商白酒指数，消费刚需+高端消费双驱动，行业景气度高",
    "008903": "广发科技先锋，聚焦科技成长，AI+半导体主线布局",
    "513180": "恒生科技ETF，港股科技龙头，估值修复空间大",
    "161130": "纳斯达克100指数，美股科技核心资产，长期增长确定性强",
    "513100": "纳指ETF，跟踪纳斯达克100，分散A股风险，全球配置",
    "164906": "交银海外中国互联网，中概股回归受益标的，估值处于历史低位",
    "006913": "消费板块持续回调超16天，估值处于历史低位，内需复苏预期下具备抄底价值",
    "004814": "近20日连跌筑底，混合策略灵活调仓，适合低位布局等待反弹",
    "512010": "医药板块集采利空出清，估值处于近年低位，长期配置性价比高",
}

CATEGORY_LABELS = {
    "gold": "黄金",
    "a_share": "A股热门",
    "overseas": "海外",
}


@router.get("/list", response_model=list[schemas.FundInfoOut])
def get_fund_list(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    if category and category not in ("gold", "a_share", "overseas"):
        return []
    return crud.get_fund_list(db, category=category)


@router.get("/{code}/nav", response_model=schemas.FundNavHistoryOut)
def get_fund_nav(
    code: str,
    limit: int = Query(30, le=100),
    db: Session = Depends(get_db),
):
    fund = crud.get_fund_by_code(db, code)
    if not fund:
        return {"code": code, "name": "", "navs": []}
    navs = crud.get_nav_history(db, code, limit=limit)
    return {
        "code": code,
        "name": fund.name,
        "navs": [
            {"nav_date": n.nav_date, "nav": n.nav,
             "accumulated_nav": n.accumulated_nav,
             "daily_return": n.daily_return}
            for n in navs
        ],
    }


@router.get("/{code}/analysis", response_model=schemas.FundAnalysisOut)
def get_fund_analysis(
    code: str,
    db: Session = Depends(get_db),
):
    fund = crud.get_fund_by_code(db, code)
    if not fund:
        return {"code": code, "name": "", "category": "",
                "recommendation_reason": ""}

    navs = crud.get_nav_history(db, code, limit=30)
    navs_sorted = sorted(navs, key=lambda n: n.nav_date, reverse=True)

    current_nav = navs_sorted[0].nav if navs_sorted else None
    daily_return = navs_sorted[0].daily_return if navs_sorted else None

    # Momentum: compare recent vs older NAV
    momentum_5d = None
    momentum_20d = None
    if len(navs_sorted) >= 5:
        momentum_5d = round(
            (navs_sorted[0].nav - navs_sorted[4].nav) / navs_sorted[4].nav * 100, 2
        )
    if len(navs_sorted) >= 20:
        momentum_20d = round(
            (navs_sorted[0].nav - navs_sorted[19].nav) / navs_sorted[19].nav * 100, 2
        )

    lot_size = 100
    lot_price = round(current_nav * lot_size, 2) if current_nav else None

    return {
        "code": code,
        "name": fund.name,
        "category": fund.category,
        "current_nav": current_nav,
        "daily_return": daily_return,
        "momentum_5d": momentum_5d,
        "momentum_20d": momentum_20d,
        "recommendation_reason": RECOMMENDATION_REASONS.get(code, ""),
        "lot_size": lot_size,
        "lot_price": lot_price,
    }
