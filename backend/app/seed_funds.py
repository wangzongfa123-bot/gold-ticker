import asyncio
from app.database import SessionLocal
from app import crud
from app.services.fund_discovery import (
    fetch_popular_funds,
    fetch_qdii_funds,
    is_gold_fund,
)

# Always keep gold ETFs in the list
ALWAYS_INCLUDE = {"518880", "159937"}  # gold ETFs


def _categorize_and_select(popular: list, qdii: list) -> list[dict]:
    """Select and categorize funds, avoiding duplicates."""
    seen = set()
    result = []

    # First: always include gold ETFs
    for fund in popular:
        if fund["code"] in ALWAYS_INCLUDE and fund["code"] not in seen:
            seen.add(fund["code"])
            result.append({**fund, "category": "gold"})

    # Gold funds from popular list
    for fund in popular:
        if fund["code"] not in seen and is_gold_fund(fund["name"]):
            seen.add(fund["code"])
            result.append({**fund, "category": "gold"})

    # QDII / overseas
    for fund in qdii:
        if fund["code"] not in seen:
            seen.add(fund["code"])
            result.append({**fund, "category": "overseas"})

    # A-share popular (top performing, not already included)
    a_share_count = 0
    for fund in popular:
        if fund["code"] not in seen and a_share_count < 10:
            seen.add(fund["code"])
            result.append({**fund, "category": "a_share"})
            a_share_count += 1

    return result


async def discover_funds() -> list[dict]:
    """Auto-discover funds from eastmoney rankings."""
    popular, qdii = await asyncio.gather(
        fetch_popular_funds(),
        fetch_qdii_funds(),
    )
    return _categorize_and_select(popular, qdii)


async def seed_funds():
    """Auto-seed funds from eastmoney, pulling NAV for each."""
    from app.services.fund_nav import fetch_history_nav

    discovered = await discover_funds()

    db = SessionLocal()
    try:
        added = 0
        for fund in discovered:
            # Seed fund info
            fund_entry = {
                "code": fund["code"],
                "name": fund["name"],
                "category": fund["category"],
            }
            crud.seed_fund_info(db, [fund_entry])

            # Generate and store reason
            reason = fund.get("reason", "")
            if not reason:
                from app.services.fund_discovery import generate_reason

                reason = generate_reason(fund, fund["category"])
            crud.update_fund_reason(db, fund["code"], reason)

            # Fetch NAV history
            navs = await fetch_history_nav(fund["code"], page=1, page_size=30)
            if navs:
                for n in navs:
                    crud.upsert_nav(
                        db,
                        fund["code"],
                        n["nav_date"],
                        n["nav"],
                        n.get("accumulated_nav"),
                        n.get("daily_return"),
                    )
            added += 1
            print(f"[Seed] Fund {fund['code']} {fund['name']} ({fund['category']})")

        print(f"[Seed] Auto-discovered and seeded {added} funds")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(seed_funds())
