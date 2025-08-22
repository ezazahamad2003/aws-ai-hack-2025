# server.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Example tool: check_status
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
    # Vapi expects JSON result payload the model can read
    return {"ok": True, "data": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
