import json
from datetime import date, timedelta
from pathlib import Path

from psycopg2.extras import execute_values

from db import get_conn


def parse_date_range(label: str) -> tuple[date, date, str]:
    """Return (start_date, end_date, notes).

    Supports:
    - 'YYYY-MM-DD:YYYY-MM-DD'
    - GA4-style '30daysAgo:yesterday' (computed at load time)
    """
    if ":" in label:
        a, b = label.split(":", 1)
        # ISO range
        if len(a) == 10 and len(b) == 10 and a[4] == "-" and b[4] == "-":
            return date.fromisoformat(a), date.fromisoformat(b), ""

        # Relative GA4 range (best-effort)
        if a == "30daysAgo" and b == "yesterday":
            end_d = date.today() - timedelta(days=1)
            start_d = end_d - timedelta(days=30)
            return start_d, end_d, "computed from 30daysAgo:yesterday at load time"

    # Fallback: treat as unknown and still load
    end_d = date.today() - timedelta(days=1)
    start_d = end_d - timedelta(days=30)
    return start_d, end_d, f"unparsed date_range '{label}', defaulted to last 30 days ending yesterday"


def load_file(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def insert_data_run(cur, source: str, brand: str, start_d: date, end_d: date, notes: str) -> int:
    cur.execute(
        """
        INSERT INTO data_runs (source, brand, start_date, end_date, notes)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (source, brand, start_d, end_d, notes or None),
    )
    return int(cur.fetchone()[0])


def main():
    files = [
        Path("data/ga4_run_report_dxfferent_flat.json"),
        Path("data/ga4_run_report_proxuma_flat.json"),
    ]

    total_inserted = 0
    with get_conn() as conn:
        with conn.cursor() as cur:
            for fp in files:
                rows = load_file(fp)
                if not rows:
                    print(f"Skipping {fp} (no rows)")
                    continue

                brand = rows[0].get("brand")
                date_range = rows[0].get("date_range", "unknown:unknown")
                start_d, end_d, notes = parse_date_range(date_range)

                run_id = insert_data_run(cur, "ga4", brand, start_d, end_d, f"traffic report; {notes}".strip())

                values = []
                for r in rows:
                    values.append(
                        (
                            run_id,
                            r.get("landingPagePlusQueryString") or "",
                            r.get("sessionSource") or "",
                            r.get("sessionMedium") or "",
                            None,  # campaign not captured in current GA4 report
                            int(r.get("sessions", 0)),
                            int(r.get("totalUsers", 0)),
                            None,  # conversions not captured in current GA4 report
                            start_d,
                            end_d,
                        )
                    )

                execute_values(
                    cur,
                    """
                    INSERT INTO traffic_events (
                        run_id, page, source, medium, campaign,
                        sessions, users, conversions,
                        start_date, end_date
                    )
                    VALUES %s
                    """,
                    values,
                    page_size=2000,
                )

                inserted = len(values)
                total_inserted += inserted
                print(f"Loaded {inserted} rows from {fp.name} (run_id={run_id})")

        conn.commit()

    print(f"Done. Inserted total traffic_events rows: {total_inserted}")


if __name__ == "__main__":
    main()
