import json, requests, os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("VAPI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
payload = { "assistantId": ASSISTANT_ID }

resp = requests.post("https://api.vapi.ai/session", headers=headers, data=json.dumps(payload))
print(resp.status_code, resp.text)
