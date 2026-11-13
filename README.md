# Erma Tour & Travel

Web application for **Erma Tour & Travel**, an Ethiopia-based tour and travel company. Built with **Python (FastAPI)**, **PostgreSQL**, and server-rendered pages (Jinja2).

## Features
- Public website: home, tours catalog, tour detail, about Ethiopia, contact
- Tour booking requests and contact inquiries (stored in PostgreSQL)
- REST API: `/api/tours`, `/api/bookings`, `/api/inquiries`, `/api/health`
- Sample Ethiopian tours seeded on first run (Lalibela, Simien Mountains, Danakil, Omo Valley, Addis Ababa, Bale Mountains)

## Prerequisites
- Python 3.11+
- PostgreSQL running locally or remotely

## Setup
1. **Create and activate a virtual environment**
   ```powershell
   cd "C:\Users\NID\Documents\Erma"
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```powershell
   copy .env.example .env
   ```
   Edit `.env` and set `DATABASE_URL` to your PostgreSQL instance, e.g.
   ```
   DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/erma_tours
   ```
   Also set a strong `SECRET_KEY`.

4. **Create the database** (in `psql` or pgAdmin)
   ```sql
   CREATE DATABASE erma_tours;
   ```

5. **Run the app**
   ```powershell
   python -m uvicorn app.main:app --reload --port 8000
   ```
   Open http://localhost:8000 — tables are created and sample tours are seeded automatically on first start.

## API
- `GET /api/health` — health check
- `GET /api/tours` — list tours (`?featured=true` for featured)
- `GET /api/tours/{id}` — tour detail
- `POST /api/tours` — create a tour
- `POST /api/bookings` — submit a booking request
- `POST /api/inquiries` — submit a contact inquiry

## Project structure
```
app/
  main.py        # FastAPI app & startup
  config.py      # settings (.env)
  database.py    # SQLAlchemy engine/session
  models.py      # Tour, Booking, Inquiry
  schemas.py     # Pydantic schemas
  crud.py        # DB operations
  seed.py        # sample data
  routers/       # pages, tours, bookings APIs
  templates/     # Jinja2 HTML pages
  static/css/    # styles
```

## Next steps
- Add admin authentication and a dashboard to manage tours/bookings
- Integrate payments and email/SMS notifications
- Add image uploads and multilingual support (Amharic/English)
- Deploy (e.g. Render/Railway + managed Postgres like Neon/Supabase)
