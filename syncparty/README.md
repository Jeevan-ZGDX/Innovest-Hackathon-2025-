# SyncParty (Full Stack)

Turn a room of phones into a pop-up surround system. This repository contains:
- `server` (Django + DRF + Channels) for auth, party management, and realtime sync
- `client/frontend` (Vite + React + TS + Tailwind) for the device grid UI and playback controls

## Features (MVP)
- JWT authentication and user registration
- Create/join parties via code
- Map devices onto a grid simulating spatial layout
- WebSocket realtime events: device updates, play/pause/seek/track
- Scheduled playback start using timestamp for low-latency sync

## Quickstart

Backend:
```
cd /workspace/syncparty/server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Frontend:
```
cd /workspace/syncparty/client/frontend
npm i
npm run dev -- --host
```

Open the app, register/login, create a party, and share the code. Use a public-accessible audio URL to test sync.

## Notes
- For production, run Channels with Redis and configure `CHANNEL_LAYERS` accordingly.
- Add TLS and replace the in-memory channel layer.
- Replace plain audio URLs with a music API (e.g., YouTube, SoundCloud, or open-source catalog) and implement local caching or chunked prefetch to reduce start latency.