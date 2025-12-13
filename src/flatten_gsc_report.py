import json
import os
import argparse
from datetime import date

"""Flatten Google Search Console (GSC) searchanalytics.query output.

Input (raw):
{
  "rows": [
    {
      "keys": ["<page>", "<query>"],
      "clicks": 0,
      "impressions": 0,
      "ctr": 0.0,
      "position": 0.0
    },
    ...
  ]
}

Output (flat): list[dict]
{
  "brand": "proxuma",
  "date_range": "YYYY-MM-DD:YYYY-MM-DD",
  "page": "...",
  "query": "...",
  "clicks": 0,
  "impressions": 0,
  "ctr": 0.0,
  "position": 0.0
}

Notes:
- Assumes dimensions requested were ["page", "query"] in that order.
- If a row has missing keys, it is skipped.
"""


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--brand", required=True, help="Brand label, e.g. proxuma or dxfferent")
    p.add_argument("--in", dest="in_path", required=True, help="Path to raw GSC json, e.g. data/gsc_proxuma_raw.json")
    p.add_argument("--out", dest="out_path", required=True, help="Path to output flat json, e.g. data/gsc_proxuma_flat.json")
    p.add_argument("--start", required=False, help="Start date YYYY-MM-DD (optional; used for date_range)")
    p.add_argument("--end", required=False, help="End date YYYY-MM-DD (optional; used for date_range)")
    return p.parse_args()


def safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def main():
    args = parse_args()

    with open(args.in_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    rows = raw.get("rows", [])

    # date_range is optional; if not provided, still emit a reasonable label
    if args.start and args.end:
        date_range = f"{args.start}:{args.end}"
    else:
        # unknown range; still useful for ingestion/debugging
        date_range = "unknown:unknown"

    flat = []
    for r in rows:
        keys = r.get("keys") or []
        if len(keys) < 2:
            continue
        page, query = keys[0], keys[1]

        flat.append(
            {
                "brand": args.brand,
                "date_range": date_range,
                "page": page,
                "query": query,
                "clicks": safe_int(r.get("clicks", 0)),
                "impressions": safe_int(r.get("impressions", 0)),
                "ctr": safe_float(r.get("ctr", 0.0)),
                "position": safe_float(r.get("position", 0.0)),
            }
        )

    os.makedirs(os.path.dirname(args.out_path) or ".", exist_ok=True)
    with open(args.out_path, "w", encoding="utf-8") as f:
        json.dump(flat, f, indent=2)

    print(f"Flattened {len(rows)} raw rows -> {len(flat)} flat rows")
    print(f"Wrote: {args.out_path}")


if __name__ == "__main__":
    main()
