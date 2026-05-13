# SensorFlow

A full-stack IoT monitoring platform. Register devices, send readings via API key, set thresholds, and get real-time alerts on a live dashboard.

Built this because most junior portfolios have the same todo app or weather app. IoT + WebSockets felt like something closer to what actually shows up in job postings.

---

## What it does

- Register temperature, humidity, CO2, or pressure sensors
- Each device gets an API key — readings are sent via POST request (simulating a real sensor)
- Set min/max thresholds per device
- When a reading crosses a threshold, an alert is created automatically
- The dashboard updates in real time via WebSocket — no refresh needed

---

## Live demo

| Service | URL |
|---|---|
| Frontend | https://sensorflow-frontend.vercel.app |
| Backend API | https://sensorflow-backend-production.up.railway.app/docs |

To see it in action, create an account, add a device, grab its API key, and run the simulator below.

---

## Simulating a device

No hardware needed. This script sends readings every 5 seconds and will trigger alerts if you set thresholds on your device:

```python
import requests
import random
import time

API_KEY = "your-device-api-key"
URL = "https://sensorflow-backend-production.up.railway.app/api/readings"

while True:
    value = random.uniform(15, 45)  # adjust range to cross your thresholds
    response = requests.post(URL, json={"value": value}, headers={"X-API-Key": API_KEY})
    print(f"Sent: {value:.2f} → {response.status_code}")
    time.sleep(5)
```

Run it, keep the dashboard open, and watch readings and alerts come in live.

---

## Tech stack

**Backend**
- FastAPI — async, fast, automatic docs at `/docs`
- PostgreSQL (Neon) + SQLAlchemy 2.0 + Alembic migrations
- JWT auth with `python-jose`, passwords hashed with `argon2`
- WebSockets for real-time push to the frontend

**Frontend**
- React 18 + TypeScript + Vite
- Zustand for auth state, Axios for API calls
- Recharts for sensor data visualization
- react-hot-toast for alert notifications

**Infrastructure**
- Docker + Compose for local development
- Railway (backend), Vercel (frontend), Neon (database)
- GitHub Actions CI — runs the full test suite on every push to main

---

## Architecture

```
React Dashboard
      │
      ├── REST (Axios) ──────────► FastAPI
      │                               │
      └── WebSocket ─────────────►    ├── SQLAlchemy → PostgreSQL (Neon)
                                      └── ConnectionManager (broadcasts alerts)
```

A few decisions worth noting:

- **Routes → Services → DB** — no repository layer, kept it simple on purpose
- **Single commit per operation** — `db.flush()` to get the reading ID before creating the alert, then one `db.commit()` at the end. Avoids partial writes.
- **Always 404, never 403** — if a user tries to access another user's device, they get 404. No information leakage about what exists.
- **WebSocket auth via JWT query param** — browser WebSocket API doesn't support custom headers, so the token goes in `?token=`

---

## Running locally

**Prerequisites:** Docker, Python 3.11, Node 18+

```bash
# Clone both repos
git clone https://github.com/azizfatnassi/sensorflow-backend
git clone https://github.com/azizfatnassi/sensorflow-frontend

# Start the backend
cd sensorflow-backend
cp .env.example .env   # fill in your values
docker compose up --build

# Start the frontend (separate terminal)
cd sensorflow-frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`, backend on `http://localhost:8000`.

API docs available at `http://localhost:8000/docs`.

---

## Running tests

```bash
cd backend
pytest tests/ -v
```

13 tests covering auth, device management, and reading ingestion with threshold detection. Uses SQLite in-memory so no database setup needed.

---

## Project structure

```
backend/
├── app/
│   ├── api/routes/       # auth, devices, readings, alerts, websocket
│   ├── services/         # business logic layer
│   ├── schemas/          # Pydantic models (separate from DB models)
│   ├── db/
│   │   ├── models/       # SQLAlchemy models
│   │   └── session.py    # engine + session dependency
│   ├── core/             # security, config, shared dependencies
│   └── websocket/        # ConnectionManager
└── tests/

frontend/
└── src/
    ├── api/              # Axios instance + interceptors
    ├── store/            # Zustand auth store
    ├── hooks/            # useWebSocket
    └── pages/            # Login, Register, Dashboard
```

---

## CI/CD

Every push to `main` on the backend repo:
1. Spins up a PostgreSQL service container
2. Runs the full test suite
3. On success, Railway picks up the new commit and redeploys (runs `alembic upgrade head` before starting)

Vercel deploys the frontend automatically on push.
