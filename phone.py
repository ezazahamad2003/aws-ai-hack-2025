# phone.py (fixed)
import os, sys, json, requests
from dotenv import load_dotenv

load_dotenv()
API_KEY      = os.getenv("VAPI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")  # 37ad9a27-...
PHONE_ID     = "3fcde98e-46b1-4732-aea4-5bd000568488"  # your Twilio/Vapi number id

if len(sys.argv) < 2:
    print("Usage: python phone.py +1DESTNUMBER")
    raise SystemExit(1)

dest = sys.argv[1]  # e.g., +18786730209

payload = {
  "assistantId": ASSISTANT_ID,
  "phoneNumberId": PHONE_ID,
  "customer": { "number": dest }           # <-- KEY FIX
}

resp = requests.post(
  "https://api.vapi.ai/call",
  headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
  data=json.dumps(payload),
  timeout=30
)
print(resp.status_code, resp.text)
