# Placement Portal Application — V2

Flask REST API + JWT auth + Redis caching + Celery jobs. Vue 3 SPA frontend
(CDN, no build step), served directly by Flask — one process, one port.

## Tech stack
Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Caching (Redis), Celery,
Redis, SQLite, Vue 3, Vue Router 4, Axios, Bootstrap 5. Nothing outside the
mandatory list.

## Run it (with a virtual environment)

```bash
# 1. Redis — needed for caching + as the Celery broker
sudo apt-get install redis-server      # skip if already installed
redis-server --daemonize yes

# 2. Backend, inside a venv
cd backend
python3 -m venv venv
source venv/bin/activate               # venv\Scripts\activate on Windows
pip install -r requirements.txt
python3 app.py                         # runs on http://localhost:5001
```

Open **http://localhost:5001** — Flask serves the Vue frontend directly, so
that's the only URL you need. First run creates `placement.db` and seeds
the admin user: `admin / admin@123`.

```bash
# 3. Celery worker + beat — two more terminals, from backend/, venv activated
celery -A celery_worker.celery worker --loglevel=info
celery -A celery_worker.celery beat --loglevel=info
```
Worker runs the CSV export job. Beat fires the two scheduled jobs (daily
reminders, monthly report). Without `GCHAT_WEBHOOK_URL` / `MAIL_*` env vars
set, both print to the worker console instead of failing — fine for a local
demo.

## Manually verifying every functionality (what to check for the viva)

1. **Admin login** — `admin / admin@123`. No register route exists for admin.
2. **Company register** → shows up under Admin's "Pending Company Approvals".
   Try logging in as that company before approval — blocked.
3. **Admin approves company** → company can now log in.
4. **Company creates a drive** with `min_cgpa` / `max_backlogs` /
   `eligible_branches` set → shows under Admin's "Pending Drive Approvals".
5. **Admin approves drive** → now visible on the student dashboard.
6. **Register a student below the CGPA cutoff** → dashboard shows the drive
   greyed out with the reason, and hitting Apply is rejected server-side too
   (not just hidden in the UI).
7. **Register a qualifying student** → Apply succeeds. Apply again on the
   same drive → blocked (duplicate).
8. **Company marks the applicant "Selected"** → a `Placement` row is created
   automatically. Student's History page now shows it under Placement History.
9. **Student triggers CSV Export** from History page → watch the Celery
   worker terminal print the export + "would send" GChat alert, file lands
   in `backend/static/exports/`.
10. **Admin blacklist/unblacklist, delete** on both students and companies —
    confirm blacklisted users can't log in.
11. **Redis caching** — hit the admin dashboard twice quickly; second call
    is served from cache (`admin_dashboard_stats` key, 30s TTL). Create a
    new drive and reload — cache is busted, new numbers show immediately.

Every one of these was run end-to-end against a live server before this
handoff (not just the in-code logic) — auth, eligibility gating, duplicate
blocking, placement auto-creation, and caching all confirmed over real HTTP.
