# test_assistant.py
import os, requests, json
from dotenv import load_dotenv

load_dotenv()

aid = os.getenv("ASSISTANT_ID") or "7ae40ce4-5add-4364-83e2-da79787afaf2"
key = os.getenv("VAPI_API_KEY")

r = requests.get(
    f"https://api.vapi.ai/assistant/{aid}",
    headers={"Authorization": f"Bearer {key}"},
    timeout=30
)

print("HTTP:", r.status_code)
data = r.json()

print("\nAssistant ID:", aid)
print("Name:", data.get("name"))

msgs = data.get("model", {}).get("messages", [])
print("\nSystem prompt snippet:")
print((msgs[0]["content"][:300] if msgs else "NONE"))

tools = data.get("model", {}).get("tools", [])
print("\nTool URL:", (tools[0].get("url") if tools else "NONE"))

print("\nFirst Message:", data.get("firstMessage"))
