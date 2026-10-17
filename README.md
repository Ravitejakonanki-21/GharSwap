# GharSwap

A free, reciprocal home-stay exchange. Travelers host each other and pay with **guest-night credits** instead of money. First launch cities are Goa and Pondicherry; the data model is city-agnostic.

1 credit = 1 guest night.

## Stack

- Backend: Django 5, Django REST Framework, JWT (`simplejwt`), PostgreSQL (SQLite locally)
- Frontend: React, Vite, React Router, Axios
- Deploy: Render (API) and Vercel (web)

## Local setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

API: http://localhost:8000/api/v1/health/

Optional Postgres via Docker:

```bash
cd backend
docker compose up db
# then set DATABASE_URL in backend/.env
```

Full stack with Docker (API + Postgres):

```bash
cd backend
docker compose up --build
```

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

App: http://localhost:5173

### Tests

```bash
cd backend
.venv/bin/pytest -q
```

## Demo accounts

Password for all seeded users: `DemoPass123!`

| Role | Email |
| --- | --- |
| Goa host | anita.goa@gharswap.demo |
| Pondicherry host | ravi.pondy@gharswap.demo |
| Traveler | meera.guest@gharswap.demo |

Each new real user still gets **2 signup-bonus credits**. Seeded users also get a small adjustment so you can accept a stay immediately.

## Credit rules

- Balance is the sum of append-only `CreditLedger` rows. It is never stored as an editable field.
- A guest may request a stay only if **available** credits cover `nights × guests`.
- Available = ledger balance minus credits reserved by **accepted** stays.
- On accept, credits are reserved (no ledger write yet). On complete, the guest is debited and the host is credited in one transaction. Cancel or decline releases the reservation.
- Hosts cannot request their own listing. Overlapping accepted stays on one listing are rejected.
- Blocked users cannot see or request each other. Only participants of a completed stay can review, once each.

## API (`/api/v1/`)

- Auth: `POST /auth/register/`, `POST /auth/login/`, `POST /auth/refresh/`, `GET|PATCH /auth/me/`
- Profiles: `GET|PATCH /profiles/me/`, `GET /profiles/<user_id>/`
- Listings: `GET|POST /listings/`, `GET /listings/mine/`, `GET|PATCH|DELETE /listings/<id>/`
- Availability: `GET|POST /listings/<id>/availability/`, `DELETE /availability/<id>/`
- Stay requests: `GET|POST /stay-requests/?role=guest|host`, actions `accept|decline|cancel|complete`
- Credits: `GET /credits/`, `GET /credits/ledger/`
- Reviews: `POST /reviews/`, `GET /users/<user_id>/reviews/`
- Safety: `POST /reports/`, `GET|POST /blocks/`, `DELETE /blocks/<user_id>/`

## Deploy

### Render (backend)

1. Create a Web Service from this repo, root directory `backend`, or use `render.yaml`.
2. Attach a Postgres database and set `DATABASE_URL`.
3. Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, `DJANGO_ALLOWED_HOSTS` to your Render host, and `CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS` to the Vercel URL (`https://your-app.vercel.app`).
4. Start command is `./entrypoint.sh` (migrate, collectstatic, gunicorn).

### Vercel (frontend)

1. Import the repo, set the root directory to `frontend`.
2. Build command `npm run build`, output `dist`.
3. Set `VITE_API_URL` to `https://your-api.onrender.com/api/v1`.

## Defaults chosen

- Email is the username. Phone is optional.
- Exact street addresses are never stored; listings only keep a neighborhood (`address_area`).
- Reservation is computed from accepted stays rather than writing a temporary ledger row, so the ledger stays a true history of settled credits.
- Public listing search is unauthenticated; profiles, requests, and credits require login.

## Next

- Photo uploads on listing create in the UI (API already supports `/listings/<id>/photos/`)
- Email verification and ID verification workflow
- In-app messaging after a stay is accepted
- Production object storage for media (S3/R2) instead of local disks on Render
