# Release Checklist (Phase 1)

## 1) Environment

- [ ] `cp .env.example .env`
- [ ] Configure admin/sales credentials in `.env`
- [ ] Optional: configure `DATABASE_URL` for PostgreSQL

## 2) Quality Gates

- [ ] `make lint`
- [ ] `make test`
- [ ] Verify API docs: `http://127.0.0.1:8000/docs`

## 3) Functional Smoke

- [ ] Admin login works
- [ ] Sales login works
- [ ] Intake -> assessment -> recommendation -> report flow works
- [ ] Red-flag path blocks personalized recommendation
- [ ] Follow-up close -> re-assess works
- [ ] Export JSON report works
- [ ] Export ops summary markdown works

## 4) Security/Compliance

- [ ] Admin endpoints require admin token
- [ ] Audit logs are generated for write operations
- [ ] Reports include disclaimer
- [ ] Forbidden/diagnostic language controls are active in templates

## 5) Deployment

- [ ] `docker compose up --build` succeeds
- [ ] `GET /api/v1/health` returns healthy
- [ ] Persisted volumes mounted: `data/` and `exports/`

## 6) Handoff

- [ ] Share API endpoint list with stakeholders
- [ ] Share demo credentials policy (rotate defaults)
- [ ] Archive first pilot metrics snapshot
