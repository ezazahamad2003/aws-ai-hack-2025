# create_assistant.py  (remove maxOutputTokens)
import os, json, requests, re
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("VAPI_API_KEY")
TOOL_ID  = os.getenv("TOOL_ID")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

if not API_KEY:
    raise SystemExit("Missing VAPI_API_KEY in .env")
if not TOOL_ID:
    raise SystemExit("Missing TOOL_ID in .env (run create_tool.py first)")

with open("prompt.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

payload = {
    "name": "Calex Supply Chain Agent",
    "firstMessage": "Hey—what PO do you want me to check?",
    "model": {
        "provider": "google",
        "model": "gemini-1.5-flash",
        "messages": [
            {"role": "system", "content": system_prompt}
        ],
        "toolIds": [TOOL_ID],
        "temperature": 0.4
        # NOTE: no maxOutputTokens here
    },
    "voice": {
        "provider": "11labs",
        "voiceId": VOICE_ID
    },
    "transcriber": {
        "provider": "deepgram",
        "model": "nova-2-general"
    }
}

resp = requests.post("https://api.vapi.ai/assistant", headers=headers, data=json.dumps(payload), timeout=30)
print(resp.status_code, resp.text)

# If created, auto-write ASSISTANT_ID to .env
try:
    data = resp.json()
    asst_id = data.get("id")
    if asst_id:
        print("ASSISTANT_ID:", asst_id)
        env_path = ".env"
        if os.path.exists(env_path):
            txt = open(env_path, "r", encoding="utf-8").read()
            if re.search(r"^ASSISTANT_ID=.*", txt, flags=re.M):
                txt = re.sub(r"^ASSISTANT_ID=.*", f"ASSISTANT_ID={asst_id}", txt, flags=re.M)
            else:
                if not txt.endswith("\n"):
                    txt += "\n"
                txt += f"ASSISTANT_ID={asst_id}\n"
            open(env_path, "w", encoding="utf-8").write(txt)
            print("Updated .env with ASSISTANT_ID")
except Exception:
    pass
