🏗️ Phase 1 — Project Setup & Infrastructure
Goal: Everything running locally, nothing broken before we write features.

Folder structure created
Python venv + dependencies installed
Django project + api app created
PostgreSQL running via Docker Compose
Django connected to PostgreSQL
Django dev server running on localhost:8000
Vue+ Vite + Tailwind running on localhost:5173

End result: Two servers running, talking to one DB. No features yet, just the skeleton.

🗄️ Phase 2 — Database Models & Seed Data
Goal: Define your tables in Django, run migrations, seed car data.

Car model (name, base rate, extra km rate, extra hr rate)
Session model (party names, created date)
DutySlipEntry model (date, car, kms, times, bhatta, parking)
Run migrations (creates tables in PostgreSQL)
Seed car catalogue (Ute, Camry, HiAce, etc.)
Register models in Django Admin (free UI to inspect data)

End result: Tables exist in DB, car data is seeded, you can view it in Django Admin.

⚙️ Phase 3 — Backend API (Django REST Framework)
Goal: All REST endpoints working, testable via Postman/Bruno.

CarSerializer + GET /api/cars/
SessionSerializer + POST /api/sessions/ + GET /api/sessions/
GET /api/sessions/{id}/ (session + all its entries)
DutySlipEntrySerializer + POST /api/sessions/{id}/entries/
PUT /api/entries/{id}/ + DELETE /api/entries/{id}/
Invoice computation logic (extra kms, extra hrs, totals per row, grand total)
GET /api/sessions/{id}/invoice/

End result: Full API working, all business logic computed correctly in the backend.

🎨 Phase 4 — Frontend (Vue + Vite + Tailwind)
Goal: Fully working UI connected to the real API.

Axios setup + base API config
Sessions list page — all parties, click to open
Create Session page — enter party names, pick start date
Duty Slip page — add day rows (date, car, kms, times, bhatta, parking), edit/delete rows
Invoice page — computed table, all rows, grand total, print button
Dark minimal UI throughout (clean, utilitarian)

End result: Full working app in the browser.

🖨️ Phase 5 — Invoice PDF & Print
Goal: Generate a clean printable/downloadable invoice.

Print-friendly CSS for invoice page
PDF export (using a library like react-pdf or browser print)
Invoice shows company name, party name, all rows, grand total

End result: You can hand a proper invoice to a client.

🐳 Phase 6 — Full Docker Setup
Goal: One command starts everything.

Dockerfile for Django backend
Dockerfile for React frontend
docker-compose.yml runs all three (DB + backend + frontend)
Environment variables properly handled

End result: docker compose up → entire app running.

🚀 Phase 7 — Deployment (Optional)
Goal: App accessible on the internet.

Deploy to a VPS (DigitalOcean / Hetzner)
Nginx as reverse proxy
SSL certificate
Production settings in Django

# 🏗️ Project Roadmap — Duty Slip & Invoice System

---

## 🏗️ Phase 1 — Project Setup & Infrastructure

**Goal:**

Everything running locally, nothing broken before we write features.

### Setup Tasks

- Create project folder structure
- Setup Python virtual environment (`venv`)
- Install dependencies
- Create Django project + `api` app
- Setup PostgreSQL via Docker Compose
- Connect Django to PostgreSQL
- Run Django dev server (`localhost:8000`)
- Setup Vue + Vite + Tailwind (`localhost:5173`)

### ✅ End Result

- Two servers running:
    - Backend (Django)
    - Frontend (Vue)
- Both connected to a single PostgreSQL database
- No features yet — just a working skeleton

---

## 🗄️ Phase 2 — Database Models & Seed Data

**Goal:**

Define database structure and populate initial data.

### Models

- **Car**
    - `name`
    - `base_rate`
    - `extra_km_rate`
    - `extra_hr_rate`
- **Session**
    - `party_names`
    - `created_date`
- **DutySlipEntry**
    - `date`
    - `car`
    - `kms`
    - `time_start`
    - `time_end`
    - `bhatta`
    - `parking`

### Tasks

- Run migrations (create tables in PostgreSQL)
- Seed car catalogue:
    - Ute
    - Camry
    - HiAce
    - etc.
- Register models in Django Admin

### ✅ End Result

- Database tables created
- Seed data available
- Data viewable via Django Admin UI

---

## ⚙️ Phase 3 — Backend API (Django REST Framework)

**Goal:**

Fully functional REST API with business logic.

### Endpoints

### Cars

- `GET /api/cars/`

### Sessions

- `POST /api/sessions/`
- `GET /api/sessions/`
- `GET /api/sessions/{id}/`

### Entries

- `POST /api/sessions/{id}/entries/`
- `PUT /api/entries/{id}/`
- `DELETE /api/entries/{id}/`

### Invoice

- `GET /api/sessions/{id}/invoice/`

### Features

- Serializers for all models
- Business logic:
    - Extra km calculation
    - Extra hour calculation
    - Row totals
    - Grand total

### ✅ End Result

- Fully working backend
- Testable via Postman / Bruno
- All calculations handled server-side

---

## 🎨 Phase 4 — Frontend (Vue + Vite + Tailwind)

**Goal:**

Complete UI connected to backend API.

### Setup

- Axios configuration
- Base API URL setup

### Pages

- **Sessions List**
    - View all sessions
    - Click to open
- **Create Session**
    - Enter party names
    - Select start date
- **Duty Slip Page**
    - Add daily entries
    - Edit/delete entries
    - Fields:
        - Date
        - Car
        - KMs
        - Time
        - Bhatta
        - Parking
- **Invoice Page**
    - Computed rows
    - Grand total
    - Print button

### UI Style

- Dark theme
- Minimal, clean, utilitarian design

### ✅ End Result

- Fully working frontend
- Real-time interaction with backend
- Smooth workflow from session → entries → invoice

---

## 🖨️ Phase 5 — Invoice PDF & Print

**Goal:**

Generate professional invoices.

### Features

- Print-friendly CSS
- PDF export:
    - Browser print OR library (e.g. `react-pdf`)
- Invoice includes:
    - Company name
    - Party name
    - All entries
    - Grand total

### ✅ End Result

- Clean printable invoice
- Ready to share with clients

---

## 🐳 Phase 6 — Full Docker Setup

**Goal:**

Run entire app with one command.

### Setup

- Dockerfile for Django backend
- Dockerfile for frontend
- `docker-compose.yml` for:
    - PostgreSQL
    - Backend
    - Frontend
- Environment variables configured properly

### ✅ End Result

```
docker compose up
```

→ Entire application running

---

## 🚀 Phase 7 — Deployment (Optional)

**Goal:**

Make app accessible online.

### Steps

- Deploy to VPS (DigitalOcean / Hetzner)
- Setup Nginx as reverse proxy
- Configure SSL (HTTPS)
- Apply Django production settings

### ✅ End Result

- Live application accessible via domain
- Secure and production-ready

---

## 🧠 Final Outcome

You end up with:

- Full-stack production-ready system
- Backend with real business logic
- Clean frontend UI
- Printable invoices
- Dockerized deployment
- Optional cloud hosting

# 🏗️ Project Roadmap — Duty Slip & Invoice System

---

## 🏗️ Phase 1 — Project Setup & Infrastructure

**Goal:**

Everything running locally, nothing broken before we write features.

### Setup Tasks

- Create project folder structure
- Setup Python virtual environment (`venv`)
- Install dependencies
- Create Django project + `api` app
- Setup PostgreSQL via Docker Compose
- Connect Django to PostgreSQL
- Run Django dev server (`localhost:8000`)
- Setup Vue + Vite + Tailwind (`localhost:5173`)

### ✅ End Result

- Two servers running:
    - Backend (Django)
    - Frontend (Vue)
- Both connected to a single PostgreSQL database
- No features yet — just a working skeleton

---

## 🗄️ Phase 2 — Database Models & Seed Data

**Goal:**

Define database structure and populate initial data.

### Models

- **Car**
    - `name`
    - `base_rate`
    - `extra_km_rate`
    - `extra_hr_rate`
- **Session**
    - `party_names`
    - `created_date`
- **DutySlipEntry**
    - `date`
    - `car`
    - `kms`
    - `time_start`
    - `time_end`
    - `bhatta`
    - `parking`

### Tasks

- Run migrations (create tables in PostgreSQL)
- Seed car catalogue:
    - Ute
    - Camry
    - HiAce
    - etc.
- Register models in Django Admin

### ✅ End Result

- Database tables created
- Seed data available
- Data viewable via Django Admin UI

---

## ⚙️ Phase 3 — Backend API (Django REST Framework)

**Goal:**

Fully functional REST API with business logic.

### Endpoints

### Cars

- `GET /api/cars/`

### Sessions

- `POST /api/sessions/`
- `GET /api/sessions/`
- `GET /api/sessions/{id}/`

### Entries

- `POST /api/sessions/{id}/entries/`
- `PUT /api/entries/{id}/`
- `DELETE /api/entries/{id}/`

### Invoice

- `GET /api/sessions/{id}/invoice/`

### Features

- Serializers for all models
- Business logic:
    - Extra km calculation
    - Extra hour calculation
    - Row totals
    - Grand total

### ✅ End Result

- Fully working backend
- Testable via Postman / Bruno
- All calculations handled server-side

---

## 🎨 Phase 4 — Frontend (Vue + Vite + Tailwind)

**Goal:**

Complete UI connected to backend API.

### Setup

- Axios configuration
- Base API URL setup

### Pages

- **Sessions List**
    - View all sessions
    - Click to open
- **Create Session**
    - Enter party names
    - Select start date
- **Duty Slip Page**
    - Add daily entries
    - Edit/delete entries
    - Fields:
        - Date
        - Car
        - KMs
        - Time
        - Bhatta
        - Parking
- **Invoice Page**
    - Computed rows
    - Grand total
    - Print button

### UI Style

- Dark theme
- Minimal, clean, utilitarian design

### ✅ End Result

- Fully working frontend
- Real-time interaction with backend
- Smooth workflow from session → entries → invoice

---

## 🖨️ Phase 5 — Invoice PDF & Print

**Goal:**

Generate professional invoices.

### Features

- Print-friendly CSS
- PDF export:
    - Browser print OR library (e.g. `react-pdf`)
- Invoice includes:
    - Company name
    - Party name
    - All entries
    - Grand total

### ✅ End Result

- Clean printable invoice
- Ready to share with clients

---

## 🐳 Phase 6 — Full Docker Setup

**Goal:**

Run entire app with one command.

### Setup

- Dockerfile for Django backend
- Dockerfile for frontend
- `docker-compose.yml` for:
    - PostgreSQL
    - Backend
    - Frontend
- Environment variables configured properly

### ✅ End Result

```
docker compose up
```

→ Entire application running

---

## 🚀 Phase 7 — Deployment (Optional)

**Goal:**

Make app accessible online.

### Steps

- Deploy to VPS (DigitalOcean / Hetzner)
- Setup Nginx as reverse proxy
- Configure SSL (HTTPS)
- Apply Django production settings

### ✅ End Result

- Live application accessible via domain
- Secure and production-ready

---

## 🧠 Final Outcome

You end up with:

- Full-stack production-ready system
- Backend with real business logic
- Clean frontend UI
- Printable invoices
- Dockerized deployment
- Optional cloud hosting