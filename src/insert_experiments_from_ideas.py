import json
from pathlib import Path

from psycopg2.extras import execute_values, Json

from db import get_conn

IN_PATH = Path("data/content_ideas_from_db.json")
DEFAULT_GOAL = "increase organic visibility"

def main():
    payload = json.loads(IN_PATH.read_text(encoding="utf-8"))

    rows_to_insert = []
    for brand in ("dxfferent", "proxuma"):
        ideas = payload.get(brand, {}).get("content_ideas", [])
        for idea in ideas:
            src = idea.get("source_query") or {}
            topic = src.get("query") or "unknown"

            notes = {
                "why_now": idea.get("why_now"),
                "target_keywords": idea.get("target_keywords"),
                "cta": idea.get("cta"),
                "angle": idea.get("angle"),
                "source_query": src,
            }

            rows_to_insert.append(
                (
                    brand,
                    DEFAULT_GOAL,
                    topic,
                    idea.get("content_type") or "unknown",
                    idea.get("title") or "untitled",
                    Json(notes),
                )
            )

    if not rows_to_insert:
        print("No ideas found to insert.")
        return

    with get_conn() as conn:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO content_experiments
                  (brand, goal, topic, content_type, title, notes)
                VALUES %s
                """,
                rows_to_insert,
                page_size=500,
            )
        conn.commit()

    print(f"✅ Inserted {len(rows_to_insert)} experiments into content_experiments")

if __name__ == "__main__":
    main()
