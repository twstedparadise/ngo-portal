# NGO Portal (Django) — GPS Check-In MVP

Production-ready MVP using **Django templates** (no React) with:
- Secure login (Django auth)
- Role-based dashboards (Admin / Field Officer / Program Manager / Finance Officer)
- GPS check-in/out with **geofencing** (Haversine distance)
- Attendance tracking and activity logs

## Quick start (SQLite dev)

### 1) Create venv + install deps

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Configure environment

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# SQLite dev default if DATABASE_URL not set
# For PostgreSQL (example):
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ngo_portal
```

### 3) Migrate + create admin

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4) Run

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Notes

- GPS requires HTTPS in most browsers. `localhost` is typically allowed for development.
- For real deployments, set `DJANGO_DEBUG=0`, a strong `DJANGO_SECRET_KEY`, and configure Postgres via `DATABASE_URL`.

