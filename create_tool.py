# create_tool.py — Vapi /tool using schema-style payload (no headers/body)
import os, json, requests, sys
from dotenv import load_dotenv

load_dotenv()
API = "https://api.vapi.ai"
KEY = os.getenv("VAPI_API_KEY")
BASE = (os.getenv("PUBLIC_BASE_URL") or "").strip()

if not KEY:
    sys.exit("Missing VAPI_API_KEY in .env")
if not BASE or not BASE.startswith("https://"):
    sys.exit("PUBLIC_BASE_URL must be your https ngrok URL (no spaces)")

url = f"{BASE.rstrip('/')}/verify-and-notify"

payload = {
    "name": "verify_and_notify",
    "description": "Verify by account_id OR (full_name + dob) and send refund email.",
    "url": url,
    "method": "POST",
    # IMPORTANT: use schema, not headers/body
    "schema": {
        "type": "object",
        "properties": {
            "account_id": {"type": "string", "description": "If provided, prefer this for verification"},
            "full_name":  {"type": "string", "description": "Full name for name+DOB verification"},
            "dob":        {"type": "string", "description": "YYYY-MM-DD for name+DOB verification"}
        }
        # no "required" ⇒ allows either path
    }
}

resp = requests.post(
    f"{API}/tool",
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    data=json.dumps(payload),
    timeout=30
)

print(resp.status_code, resp.text)
resp.raise_for_status()
tool_id = resp.json().get("id")
print("TOOL_ID:", tool_id)
