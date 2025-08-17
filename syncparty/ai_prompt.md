You are a senior full‑stack engineer. Build a high‑performance web app called "SyncParty" that turns a room of phones into a synchronized home‑theater speaker array.

Requirements
- Architecture:
  - Frontend: React + TypeScript + Tailwind, Vite bundler
  - Backend: Python Django + DRF + Channels (WebSockets); JWT auth (simplejwt); CORS enabled
  - DB: SQLite for dev; make models portable for Postgres
  - Realtime: Channels in dev uses InMemory channel layer; provide Redis config snippet for prod
- Core features:
  1) Auth: register, login, refresh; protected API routes; token storage in localStorage
  2) Parties:
     - Create party (host = current user) and generate 8‑char code
     - Join party by code; each user becomes a `PartyDevice` with label; `is_main_device` flag allowed
  3) Device grid mapping:
     - Show NxN grid (3–7). Clicking an empty cell assigns selected device to that cell; update via REST; broadcast via WebSocket `device_update`
     - Store `grid_x`, `grid_y` and optional `angle_deg` for 360° panning later
  4) Playback sync:
     - Simple audio element per device
     - WebSocket events: `track` {url}, `play` {startAtEpochMs, seekMs?}, `pause`, `seek` {seekMs}
     - On `play`, schedule `audio.play()` for the provided timestamp for low‑latency start
     - REST `playback` endpoint stores state
  5) UI/UX:
     - Three panels: Connected Devices, Device Grid, System Status; dark theme; responsive
     - Show party code, WebSocket status, quick actions
  6) Topology:
     - Connection from main device to all phones is parallel (MD -> P1..Pn). Sound traversal can be simulated visually in series ring order (P1 -> P2 -> ... -> Pn -> P1)
- Extra features to include (stubbed if needed):
  - Audio calibration ping for offset measurement
  - Ring animation to visualize series traversal
  - Export/import settings JSON
  - LAN discovery notes and hotspot mode (doc + placeholders)

Deliverables
- Django project with apps: `core` (models: Party, PartyDevice, PlaybackState), JWT endpoints, REST routes, Channels consumer
- React app with pages: auth/login, lobby (create/join), device grid dashboard, simple playback controls
- Tailwind styling and zustand or context for state
- README with dev instructions, .env example, and production notes (Redis Channels, TLS)

APIs
- POST /api/auth/register
- POST /api/auth/token, /api/auth/token/refresh
- REST router `/api/parties` with actions:
  - POST /api/parties/ (create)
  - GET /api/parties/by-code/:code
  - POST /api/parties/join-by-code
  - POST /api/parties/:id/join
  - POST /api/parties/:id/leave
  - POST /api/parties/:id/update_device
  - POST /api/parties/:id/playback
- WS: `ws://<host>/ws/party/<party_code>/` broadcasting events above

Quality
- Strong typing, clear names, guard clauses, early returns, minimal nesting, no inline comments, readable code
- Use spaces for indentation, wrap long lines, and avoid unrelated reformatting
- Include an admin registration for all models

Provide code in full, with file paths and content blocks ready to paste into a repository. Do not include binary or super long base64. Keep the code runnable immediately.