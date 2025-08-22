# server.py — your original tool + verify/email in one app
import os, json, smtplib, ssl
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, Body
from pydantic import BaseModel
import uvicorn

# (optional) load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = FastAPI(title="Vapi Server (tools + verify/email)")

# ----------------------------
# Existing tool: /tool/check_status
# ----------------------------
class CheckStatusPayload(BaseModel):
    po_id: str
    carrier: str | None = None

@app.post("/tool/check_status")
async def check_status(req: Request):
    payload = await req.json()
    data = payload.get("input", {})
    po_id = data.get("po_id")
    carrier = data.get("carrier")
    # TODO: replace with your real logic / DB / API call
    result = {
        "po_id": po_id,
        "carrier": carrier or "unknown",
        "status": "In transit",
        "eta": "2025-08-25"
    }
    # Vapi expects JSON the model can read
    return {"ok": True, "data": result}

# ----------------------------
# Verify + Email: /healthz, /verify-and-notify
# ----------------------------
DATA_PATH = Path(os.getenv("DATA_PATH", "./insurance_policies_mock.json"))
SMTP_HOST = os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "no-reply@insuremock.test")
OVERRIDE_EMAIL = os.getenv("OVERRIDE_EMAIL", "")  # e.g., you@example.com

# Load dataset once
if not DATA_PATH.exists():
    raise RuntimeError(f"DATA_PATH not found: {DATA_PATH}")
with DATA_PATH.open("r", encoding="utf-8") as f:
    blob = json.load(f)
POLICIES = blob["policies"] if "policies" in blob else blob

def find_by_account_id(account_id: str) -> Optional[Dict[str, Any]]:
    return next((r for r in POLICIES if r.get("account_id") == account_id), None)

def find_by_name_dob(full_name: str, dob: str) -> Optional[Dict[str, Any]]:
    return next(
        (r for r in POLICIES
         if r.get("holder", {}).get("full_name") == full_name
         and r.get("holder", {}).get("dob") == dob),
        None
    )

def send_email(to_addr: str, subject: str, body: str) -> Dict[str, Any]:
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        return {"ok": False, "reason": "SMTP not configured (check .env)"}
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_addr
    msg.set_content(body)
    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=ctx)
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
    return {"ok": True, "channel": "email", "to": to_addr}

class VerifyNotifyReq(BaseModel):
    # Provide ONE of these:
    account_id: Optional[str] = None
    full_name: Optional[str] = None
    dob: Optional[str] = None   # YYYY-MM-DD
    # Optional explicit destination (otherwise holder email or OVERRIDE_EMAIL)
    notify_to: Optional[str] = None

class VerifyNotifyRes(BaseModel):
    verified: bool
    method: Optional[str] = None
    said: str
    notified: Optional[bool] = None
    notify_to: Optional[str] = None
    reason: Optional[str] = None
    policy_id: Optional[str] = None
    account_id: Optional[str] = None

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/verify-and-notify", response_model=VerifyNotifyRes)
def verify_and_notify(req: VerifyNotifyReq = Body(...)):
    record = None
    method = None
    if req.account_id:
        record = find_by_account_id(req.account_id)
        method = "account_id"
    elif req.full_name and req.dob:
        record = find_by_name_dob(req.full_name, req.dob)
        method = "name_dob"

    if not record:
        return VerifyNotifyRes(
            verified=False,
            method=method,
            said="Sorry, I couldn't verify your details. Please try again on our website or check your credentials."
        )

    holder = record.get("holder", {})
    dest = OVERRIDE_EMAIL or req.notify_to or holder.get("email")
    said = "Thanks, I've verified your account. I'll send a confirmation about the refund shortly."

    email_res = send_email(
        dest,
        "Your refund request",
        f"Hi {holder.get('full_name')},\n\n"
        f"We've verified your account ({record.get('policy_id')}). "
        "Your refund will be processed within 3–5 business days.\n\n"
        "Thanks,\nSupport Team"
    )

    return VerifyNotifyRes(
        verified=True,
        method=method,
        said=said,
        notified=email_res.get("ok", False),
        notify_to=dest,
        reason=email_res.get("reason"),
        policy_id=record.get("policy_id"),
        account_id=record.get("account_id"),
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
