from googleapiclient.discovery import build
from google.auth import default
from dotenv import load_dotenv

def main():
    load_dotenv()

    creds, _ = default(scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    service = build("searchconsole", "v1", credentials=creds)

    sites = service.sites().list().execute()

    print("Available GSC sites:")
    for site in sites.get("siteEntry", []):
        print(f"- {site['siteUrl']} ({site['permissionLevel']})")

if __name__ == "__main__":
    main()
