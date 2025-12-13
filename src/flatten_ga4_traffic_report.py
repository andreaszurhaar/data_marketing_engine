import json
from pathlib import Path

BRAND = "proxuma"
DATE_RANGE = "30daysAgo:yesterday"

IN_PATH = Path("data/ga4_run_report_proxuma_raw.json")
OUT_PATH = Path("data/ga4_run_report_proxuma_flat.json")

def main():
    raw = json.loads(IN_PATH.read_text(encoding="utf-8"))
    report = raw.get("result", raw)

    dim_headers = [h["name"] for h in report.get("dimension_headers", [])]
    met_headers = [h["name"] for h in report.get("metric_headers", [])]

    required_dims = {"landingPagePlusQueryString", "sessionSource", "sessionMedium"}
    required_mets = {"sessions", "totalUsers"}

    if not required_dims.issubset(set(dim_headers)):
        raise ValueError(f"Missing required dimensions. Got {dim_headers}, need {sorted(required_dims)}")
    if not required_mets.issubset(set(met_headers)):
        raise ValueError(f"Missing required metrics. Got {met_headers}, need {sorted(required_mets)}")

    dim_idx = {name: i for i, name in enumerate(dim_headers)}
    met_idx = {name: i for i, name in enumerate(met_headers)}

    out_rows = []
    for r in report.get("rows", []):
        dim_vals = [dv.get("value") for dv in r.get("dimension_values", [])]
        met_vals = [mv.get("value") for mv in r.get("metric_values", [])]

        out_rows.append({
            "brand": BRAND,
            "date_range": DATE_RANGE,
            "landingPagePlusQueryString": dim_vals[dim_idx["landingPagePlusQueryString"]],
            "sessionSource": dim_vals[dim_idx["sessionSource"]],
            "sessionMedium": dim_vals[dim_idx["sessionMedium"]],
            "sessions": int(met_vals[met_idx["sessions"]]),
            "totalUsers": int(met_vals[met_idx["totalUsers"]]),
        })

    OUT_PATH.write_text(json.dumps(out_rows, indent=2), encoding="utf-8")
    print(f"✅ Wrote {len(out_rows)} rows to {OUT_PATH}")

if __name__ == "__main__":
    main()
