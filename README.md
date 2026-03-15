# Health Sales Nutrition Assistant (MVP)

MVP backend for the nutrition support assistant described in project review docs.

## Run

```bash
python3.13 -m venv .venv313
source .venv313/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run With Docker

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Demo page: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`

## Make Commands

```bash
make setup
make run
make test
make lint
```

API base: `http://127.0.0.1:8000/api/v1`
Swagger: `http://127.0.0.1:8000/docs`
Demo page: `http://127.0.0.1:8000/`
SQLite file: `data/nutrition_assistant.db`

## Storage Backend

Default backend is SQLite.  
Set `DATABASE_URL` to PostgreSQL DSN to switch backend:

```text
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nutrition_assistant
```

Optional bootstrap SQL for Postgres:

```bash
psql "$DATABASE_URL" -f migrations/0001_init_postgres.sql
```

## Key Rules Implemented

- Red-flag cases block personalized sales recommendations.
- Red-flag cases can only return general nutrition reference with physician-first notice.
- Every recommendation includes trigger reasons, risk notes, and confidence.
- Report output always includes disclaimer version and disclaimer text.
- Write actions are audit-logged with actor/timestamp/resource/reason/snapshot.

## Main Endpoints

- `POST /auth/login` (username/password login)
- `GET /admin/users` (admin only, list users)
- `POST /admin/users` (admin only, create user)
- `PATCH /admin/users/{user_id}/status` (admin only, enable/disable user)
- `PATCH /admin/users/{user_id}/password` (admin only, reset user password)
- `GET /question-flow`
- `PUT /question-flow` (admin only)
- `POST /customers`
- `POST /assessments`
- `POST /recommendations`
- `POST /reports`
- `POST /reports/{report_id}/export` (login required, exports JSON file)
- `GET /exports` (admin only, list export files)
- `GET /exports/{filename}` (admin only, download export file)
- `POST /ops/export-summary` (admin only, generate management summary markdown)
- `POST /follow-ups`
- `POST /follow-ups/{followup_id}/re-assess` (login required, closed follow-up only)
- `POST /compliance-events`
- `GET /audit-logs` (admin only)
- `GET /metrics/summary` (admin only)

## Login and Tokens

Use login endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Protected endpoints require:

```text
Authorization: Bearer <token-from-login>
```

Default users are auto-seeded at startup and can be overridden by env vars:

```text
NA_ADMIN_USERNAME
NA_ADMIN_PASSWORD
NA_SALES_USERNAME
NA_SALES_PASSWORD
```

See [.env.example](/Users/yzhan101/AI_WorkSpace/health_Sales/.env.example).

## Console Roles (Demo Page)

- `sales` login: can run customer intake/assessment/recommendation/report flow.
- `admin` login: can update question flow and access audit logs.
- `admin` login: can update question flow, access audit logs, and view KPI metrics panel.
- `admin` login: can also manage users (create/enable/disable) from the console.
- The demo page switches visible panels based on login role.

## Tests

```bash
source .venv313/bin/activate
pytest -q
```
