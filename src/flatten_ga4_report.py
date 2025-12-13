import json
from pathlib import Path

BRAND = "dxfferent"
DATE_RANGE = "30daysAgo:yesterday"

IN_PATH = Path("data/ga4_events_proxuma_raw.json")
OUT_PATH = Path("data/ga4_events_proxuma_flat.json")

def main():
    raw = json.loads(IN_PATH.read_text(encoding="utf-8"))

    # Depending on how Inspector saved it, your JSON may be wrapped like {"result": {...}}
    report = raw.get("result", raw)

    out_rows = []
    for r in report["rows"]:
        dims = [dv["value"] for dv in r["dimension_values"]]
        mets = [mv["value"] for mv in r["metric_values"]]

        out_rows.append({
            "brand": BRAND,
            "date_range": DATE_RANGE,
            "landingPagePlusQueryString": dims[0],
            "sessionSource": dims[1],
            "sessionMedium": dims[2],
            "sessions": int(mets[0]),
            "totalUsers": int(mets[1]),
        })

    OUT_PATH.write_text(json.dumps(out_rows, indent=2), encoding="utf-8")
    print(f"✅ Wrote {len(out_rows)} rows to {OUT_PATH}")

if __name__ == "__main__":
    main()
