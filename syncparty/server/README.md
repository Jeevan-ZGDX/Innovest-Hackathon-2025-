# SyncParty Backend

Dev quickstart:

```
cd /workspace/syncparty/server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Auth:
- POST /api/auth/token/ with username/password
- POST /api/auth/token/refresh/
- POST /api/auth/register/

Parties:
- GET /api/parties/
- POST /api/parties/ {"name": "Living Room"}
- POST /api/parties/join-by-code {"code":"ABCD1234","label":"Pixel 7"}
- POST /api/parties/{id}/update_device
- POST /api/parties/{id}/playback

WebSocket: ws://host:8000/ws/party/{party_code}/