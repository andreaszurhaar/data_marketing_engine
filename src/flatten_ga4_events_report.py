import json
from pathlib import Path

BRAND = "proxuma"
DATE_RANGE = "30daysAgo:yesterday"

IN_PATH = Path("data/ga4_events_proxuma_raw.json")
OUT_PATH = Path("data/ga4_events_proxuma_flat.json")

def main():
    raw = json.loads(IN_PATH.read_text(encoding="utf-8"))
    report = raw.get("result", raw)

    dim_headers = [h["name"] for h in report.get("dimension_headers", [])]
    met_headers = [h["name"] for h in report.get("metric_headers", [])]

    # Ensure required fields exist (order doesn't matter)
    required_dims = {"landingPagePlusQueryString", "eventName"}
    required_mets = {"eventCount", "totalUsers"}

    if not required_dims.issubset(set(dim_headers)):
        raise ValueError(f"Missing required dimensions. Got {dim_headers}, need {sorted(required_dims)}")

    if not required_mets.issubset(set(met_headers)):
        raise ValueError(f"Missing required metrics. Got {met_headers}, need {sorted(required_mets)}")

    # Build index maps (header name -> position)
    dim_idx = {name: i for i, name in enumerate(dim_headers)}
    met_idx = {name: i for i, name in enumerate(met_headers)}

    out_rows = []
    for r in report.get("rows", []):
        dim_vals = [dv.get("value") for dv in r.get("dimension_values", [])]
        met_vals = [mv.get("value") for mv in r.get("metric_values", [])]

        landing_page = dim_vals[dim_idx["landingPagePlusQueryString"]]
        event_name = dim_vals[dim_idx["eventName"]]

        event_count = int(met_vals[met_idx["eventCount"]])
        total_users = int(met_vals[met_idx["totalUsers"]])

        out_rows.append({
            "brand": BRAND,
            "date_range": DATE_RANGE,
            "landingPagePlusQueryString": landing_page,
            "eventName": event_name,
            "eventCount": event_count,
            "totalUsers": total_users,
        })

    OUT_PATH.write_text(json.dumps(out_rows, indent=2), encoding="utf-8")
    print(f"✅ Wrote {len(out_rows)} rows to {OUT_PATH}")

if __name__ == "__main__":
    main()

