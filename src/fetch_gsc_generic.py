import os
import json
from datetime import date, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

"""
Generic Google Search Console fetch script
- Fetches page x query performance data
- Saves raw output to data/gsc_<brand>_raw.json

Requirements:
- GOOGLE_APPLICATION_CREDENTIALS set (service account JSON)
- SITE_URL must exactly match a value from list_gsc_sites.py
"""

load_dotenv()

# -------- CONFIG --------
BRAND = "dxfferent"
SITE_URL = "sc-domain:dxfferent.com"
DAYS_BACK = 30
OUTPUT_PATH = f"data/gsc_{BRAND}_raw.json"

# -------- AUTH --------
creds = service_account.Credentials.from_service_account_file(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
    scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
)

service = build("searchconsole", "v1", credentials=creds)

# -------- DATE RANGE --------
end_date = date.today() - timedelta(days=1)
start_date = end_date - timedelta(days=DAYS_BACK)

# -------- REQUEST --------
request = {
    "startDate": start_date.isoformat(),
    "endDate": end_date.isoformat(),
    "dimensions": ["page", "query"],
    "rowLimit": 25000,
}

print(f"Fetching GSC data for {SITE_URL} ({start_date} → {end_date})")

response = service.searchanalytics().query(
    siteUrl=SITE_URL,
    body=request,
).execute()

# -------- SAVE RAW --------
os.makedirs("data", exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(response, f, indent=2)

rows = response.get("rows", [])
print(f"Saved {len(rows)} rows to {OUTPUT_PATH}")
