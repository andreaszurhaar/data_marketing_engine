import os
import json
from dataclasses import dataclass
from typing import Any

from psycopg2.extras import RealDictCursor

from db import get_conn


@dataclass
class Opportunity:
    query: str
    impressions: int
    clicks: int
    avg_position: float


def fetch_gsc_opportunities(brand: str, min_impressions: int, limit: int = 15) -> list[Opportunity]:
    sql = """
    SELECT
      sq.query,
      SUM(sq.impressions) AS impressions,
      SUM(sq.clicks) AS clicks,
      AVG(sq.position) AS avg_position
    FROM search_queries sq
    JOIN data_runs dr ON dr.id = sq.run_id
    WHERE dr.brand = %s
    GROUP BY sq.query
    HAVING SUM(sq.impressions) >= %s
    ORDER BY impressions DESC, clicks ASC
    LIMIT %s;
    """

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (brand, min_impressions, limit))
            rows = cur.fetchall()

    out: list[Opportunity] = []
    for r in rows:
        out.append(
            Opportunity(
                query=str(r["query"]),
                impressions=int(r["impressions"] or 0),
                clicks=int(r["clicks"] or 0),
                avg_position=float(r["avg_position"] or 0.0),
            )
        )
    return out


def fetch_top_ga4_pages(brand: str, limit: int = 10) -> list[dict[str, Any]]:
    sql = """
    SELECT
      te.page,
      SUM(te.sessions) AS sessions,
      SUM(te.users) AS users
    FROM traffic_events te
    JOIN data_runs dr ON dr.id = te.run_id
    WHERE dr.brand = %s
    GROUP BY te.page
    ORDER BY sessions DESC
    LIMIT %s;
    """

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (brand, limit))
            return cur.fetchall()


def idea_templates_for_proxuma(o: Opportunity) -> list[dict[str, Any]]:
    q = o.query.lower().strip()

    ideas = []

    # 1) High intent comparison / solution page
    if "autotask" in q or "psa" in q or "msp" in q:
        ideas.append(
            {
                "content_type": "landing_page",
                "title": f"{o.query.title()} – How Proxuma helps MSPs do it better",
                "angle": "Commercial-intent SEO page that matches the query directly and routes to a demo.",
                "target_keywords": [o.query],
                "why_now": f"{o.impressions} impressions, {o.clicks} clicks, avg position {o.avg_position:.2f}. You’re visible but not winning clicks.",
                "cta": "Book a demo",
            }
        )

    # 2) Practical guide to capture informational intent
    if q.startswith("what is") or "what is" in q:
        ideas.append(
            {
                "content_type": "blog",
                "title": f"{o.query.title()} (Explained for MSPs): features, limitations, and alternatives",
                "angle": "Educational post with a clear ‘when Proxuma is a better fit’ section.",
                "target_keywords": [o.query],
                "why_now": f"High impressions with near-zero clicks suggests title/meta + content angle mismatch.",
                "cta": "See Proxuma features",
            }
        )

    # 3) Feature-led post for mid-funnel
    if "dispatch" in q or "calendar" in q or "capacity" in q or "projects" in q:
        ideas.append(
            {
                "content_type": "blog",
                "title": f"{o.query.title()}: a practical MSP workflow (template included)",
                "angle": "Show a workflow, include screenshots/templates, end with Proxuma workflow mapping.",
                "target_keywords": [o.query],
                "why_now": f"Avg position {o.avg_position:.2f} means Google already trusts you enough to test.",
                "cta": "Try the workflow in Proxuma",
            }
        )

    # Fallback: always at least one idea
    if not ideas:
        ideas.append(
            {
                "content_type": "blog",
                "title": f"{o.query.title()}: what MSPs should consider in 2026",
                "angle": "Thoughtful buyer’s guide with a Proxuma checklist.",
                "target_keywords": [o.query],
                "why_now": f"{o.impressions} impressions indicate demand.",
                "cta": "Download the checklist",
            }
        )

    return ideas


def idea_templates_for_dxfferent(o: Opportunity) -> list[dict[str, Any]]:
    q = o.query.lower().strip()

    ideas = []

    # Dxfferent: consultancy / authority-building
    if "security officer" in q or "information security officer" in q or "it security officer" in q:
        ideas.append(
            {
                "content_type": "blog",
                "title": f"{o.query.title()}: responsibilities, pitfalls, and a 30-day onboarding plan",
                "angle": "High-intent informational content with a consultancy CTA.",
                "target_keywords": [o.query],
                "why_now": f"{o.impressions} impressions, {o.clicks} clicks; avg position {o.avg_position:.2f}. Improve CTR with clearer title/meta + better intro.",
                "cta": "Talk to a security expert",
            }
        )
        ideas.append(
            {
                "content_type": "downloadable",
                "title": f"Security Officer Starter Kit (checklist) – aligned to ISO 27001",
                "angle": "Lead magnet that matches the intent behind ‘wat doet een security officer’ queries.",
                "target_keywords": [o.query, "iso 27001"],
                "why_now": "Turn impressions into leads with a downloadable asset.",
                "cta": "Download the starter kit",
            }
        )

    if q.startswith("wat doet"):
        ideas.append(
            {
                "content_type": "blog",
                "title": "Wat doet een security officer? (met voorbeelden per type organisatie)",
                "angle": "Dutch long-form explainer with practical examples + CTA to assessment.",
                "target_keywords": [o.query],
                "why_now": f"Ranking ~{o.avg_position:.2f} but 0 clicks suggests snippet/title aren’t compelling.",
                "cta": "Plan een intake",
            }
        )

    if not ideas:
        ideas.append(
            {
                "content_type": "blog",
                "title": f"{o.query.title()}: what it is and how to implement it safely",
                "angle": "Educational post with a services section.",
                "target_keywords": [o.query],
                "why_now": f"{o.impressions} impressions indicate demand.",
                "cta": "Get expert guidance",
            }
        )

    return ideas


def generate_for_brand(brand: str) -> dict[str, Any]:
    if brand == "proxuma":
        min_impr = 50
        ideas_fn = idea_templates_for_proxuma
    else:
        min_impr = 20
        ideas_fn = idea_templates_for_dxfferent

    opps = fetch_gsc_opportunities(brand, min_impr, limit=15)
    top_pages = fetch_top_ga4_pages(brand, limit=10)

    ideas: list[dict[str, Any]] = []
    for o in opps:
        for idea in ideas_fn(o):
            idea["brand"] = brand
            idea["source_query"] = {
                "query": o.query,
                "impressions": o.impressions,
                "clicks": o.clicks,
                "avg_position": round(o.avg_position, 2),
            }
            ideas.append(idea)

    return {
        "brand": brand,
        "top_ga4_pages": top_pages,
        "gsc_opportunities": [o.__dict__ for o in opps],
        "content_ideas": ideas,
    }


def main():
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)

    report = {
        "generated_at": os.getenv("SOURCE_DATE_EPOCH"),
        "dxfferent": generate_for_brand("dxfferent"),
        "proxuma": generate_for_brand("proxuma"),
    }

    out_path = out_dir / "content_ideas_from_db.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Wrote: {out_path}")
    print("Preview (first 5 ideas per brand):")
    for brand in ("dxfferent", "proxuma"):
        ideas = report[brand]["content_ideas"][:5]
        print(f"\n== {brand} ==")
        for i, idea in enumerate(ideas, 1):
            print(f"{i}. [{idea['content_type']}] {idea['title']} — {idea['why_now']}")


if __name__ == "__main__":
    from pathlib import Path

    main()
