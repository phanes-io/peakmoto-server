# PeakMoto Feedback Proxy

FastAPI service that receives anonymous route feedback from the PeakMoto app and forwards it to a Telegram chat.

## Data received (anonymous)

- Rating (0-5)
- Profile used (`motorcycle_curvy` etc.)
- Start + end coordinates
- Distance, duration, turn count
- Optional comment
- App version

**No user ID, no device info, no tracking.** Source IPs only in volatile HTTP logs for rate-limiting (10 req/min per IP).

## Setup

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather), get the token
2. Start a chat with the bot, send `/start`
3. Get the chat ID:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getUpdates" | jq '.result[].message.chat.id'
   ```
4. Copy `.env.example` to `.env` and fill in both values
5. Deploy:
   ```bash
   docker compose up -d --build
   ```

## Endpoints

- `GET /health` → `{"status": "ok"}`
- `POST /feedback` → Accepts `FeedbackRequest` JSON, returns `{"status": "ok", "delivered": true|false}`

## Traefik

Exposed at `feedback.peakmoto.app` via the `frontend` Docker network with Cloudflare TLS.
