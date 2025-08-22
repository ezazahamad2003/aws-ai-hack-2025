import os, json, requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("VAPI_API_KEY")
BASE = os.getenv("PUBLIC_BASE_URL")

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

payload = {
  "type": "function",
  "function": {
    "name": "check_status",
    "description": "Look up PO shipping status and ETA",
    "parameters": {
      "type": "object",
      "properties": {
        "po_id": {"type": "string"},
        "carrier": {"type": "string"}
      },
      "required": ["po_id"]
    }
  },
  "server": {
    "url": f"{BASE}/tool/check_status"
  }
}

r = requests.post("https://api.vapi.ai/tool", headers=headers, data=json.dumps(payload), timeout=30)
print(r.status_code, r.text)
