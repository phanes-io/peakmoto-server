"""
PeakMoto Feedback Proxy
Receives anonymous route feedback and forwards it to a Telegram chat.
"""
import os
import time
from collections import defaultdict, deque
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("WARN: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing - feedback will be logged only")

app = FastAPI(title="PeakMoto Feedback")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Simple in-memory rate limit: max 10 requests per minute per IP
_rate_limit_window = 60
_rate_limit_max = 10
_rate_limit_data: dict = defaultdict(lambda: deque())


class Coordinate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    name: Optional[str] = None


class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=0, le=5)
    profile: str = Field(..., max_length=50)
    start: Coordinate
    end: Coordinate
    waypoints: List[Coordinate] = Field(default_factory=list, max_length=10)
    distance_km: float = Field(..., ge=0, le=10000)
    duration_min: int = Field(..., ge=0, le=10000)
    turn_count: int = Field(..., ge=0, le=5000)
    arrived: bool
    comment: Optional[str] = Field(None, max_length=500)
    app_version: Optional[str] = Field(None, max_length=20)


def check_rate_limit(ip: str) -> bool:
    now = time.time()
    q = _rate_limit_data[ip]
    while q and q[0] < now - _rate_limit_window:
        q.popleft()
    if len(q) >= _rate_limit_max:
        return False
    q.append(now)
    return True


def format_message(req: FeedbackRequest) -> str:
    stars = "⭐" * req.rating if req.rating > 0 else "—"
    status = "🏁 beendet" if req.arrived else "🛑 abgebrochen"
    lines = [
        f"{stars} ({req.rating}/5) · {status}",
        f"Profil: {req.profile}",
        f"",
        f"Start: {req.start.lat:.5f}, {req.start.lng:.5f}",
        f"Ziel:  {req.end.lat:.5f}, {req.end.lng:.5f}"
        + (f" ({req.end.name})" if req.end.name else ""),
    ]
    if req.waypoints:
        lines.append(f"Via: {len(req.waypoints)} Waypoint(s)")
    lines.append("")
    lines.append(
        f"{req.distance_km:.1f}km · {req.duration_min}min · {req.turn_count} Abbg"
    )
    if req.comment:
        lines.append("")
        lines.append(f"💬 {req.comment}")
    if req.app_version:
        lines.append("")
        lines.append(f"v{req.app_version}")
    return "\n".join(lines)


async def send_telegram(text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[FEEDBACK] {text}")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.post(
                url,
                json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            )
            return r.status_code == 200
        except Exception as e:
            print(f"[FEEDBACK] telegram send failed: {e}")
            return False


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/feedback")
async def feedback(req: FeedbackRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="rate limit exceeded")

    text = format_message(req)
    sent = await send_telegram(text)
    return {"status": "ok", "delivered": sent}
