# create_assistant.py — assistant with embedded apiRequest tool (no /tool calls)
import os, json, requests, re
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("VAPI_API_KEY")
BASE_URL = (os.getenv("PUBLIC_BASE_URL") or "").strip()
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

if not API_KEY:
    raise SystemExit("Missing VAPI_API_KEY in .env")
if not BASE_URL or not BASE_URL.startswith("https://"):
    raise SystemExit("PUBLIC_BASE_URL must be your https ngrok URL (no spaces).")

with open("prompt.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

tool = {
    "type": "apiRequest",
    "function": {"name": "verify_and_notify"},  # what the LLM will call
    "name": "verify-and-notify",                # human label
    "url": f"{BASE_URL.rstrip('/')}/verify-and-notify",
    "method": "POST",
    # headers/body are SCHEMAS (per Vapi docs), not literal request body here
    "headers": {
        "type": "object",
        "properties": {
            "Content-Type": {"type": "string", "value": "application/json"}
        }
    },
    "body": {
        "type": "object",
        "properties": {
            "account_id": {"type": "string", "description": "Account ID if provided"},
            "full_name":  {"type": "string", "description": "Full name if provided"},
            "dob":        {"type": "string", "description": "YYYY-MM-DD if provided"}
        }
        # no "required": allows either account_id OR name+dob
    },
    "timeoutSeconds": 45,
    "backoffPlan": {"type": "exponential", "maxRetries": 2, "baseDelaySeconds": 1}
}

payload = {
    "name": "AutoShield Verify & Email",  # keep <= 40 chars
    "firstMessage": (
        "Hi! I can help with your auto policy refund. "
        "I can verify you by Account ID or by your full name and date of birth. Which do you prefer?"
    ),
    "model": {
        "provider": "google",
        "model": "gemini-1.5-flash",
        "messages": [{"role": "system", "content": system_prompt}],
        "tools": [tool],           # <— embed tool here
        "temperature": 0.4
    },
    "voice": {"provider": "11labs", "voiceId": VOICE_ID},
    "transcriber": {"provider": "deepgram", "model": "nova-2-general"}
}

resp = requests.post(
    "https://api.vapi.ai/assistant",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    data=json.dumps(payload),
    timeout=30
)
print(resp.status_code, resp.text)
resp.raise_for_status()

assistant_id = resp.json().get("id")
print("ASSISTANT_ID:", assistant_id)

# write ASSISTANT_ID into .env (used by phone.py)
if assistant_id:
    env_path = ".env"
    txt = open(env_path, "r", encoding="utf-8").read()
    if re.search(r"^ASSISTANT_ID=.*", txt, flags=re.M):
        txt = re.sub(r"^ASSISTANT_ID=.*", f"ASSISTANT_ID={assistant_id}", txt, flags=re.M)
    else:
        if not txt.endswith("\n"):
            txt += "\n"
        txt += f"ASSISTANT_ID={assistant_id}\n"
    open(env_path, "w", encoding="utf-8").write(txt)
    print("Updated .env with ASSISTANT_ID")
