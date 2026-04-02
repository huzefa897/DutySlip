# DutySlip — Production Setup Guide

Fleet management and invoicing system built with Django, Vue, PostgreSQL, and Docker.

---

## Prerequisites

Before running DutySlip, make sure you have the following installed:

| Tool | Purpose | Download |
|---|---|---|
| Docker Desktop | Runs all services | [docker.com](https://www.docker.com/products/docker-desktop) |
| Git | Pull the code | [git-scm.com](https://git-scm.com) |

---

## Option A — Run via Electron App (Recommended)

The easiest way to run DutySlip is using the desktop control panel.

### 1. Download the app

Go to the [Releases page](https://github.com/huzefa897/DutySlip/releases) and download:
- **Mac:** `DutySlip-x.x.x.dmg`
- **Windows:** `DutySlip-x.x.x-Setup.exe`

### 2. Install

**Mac:**
1. Open the `.dmg` file
2. Drag DutySlip to your Applications folder
3. Open DutySlip from Applications

**Windows:**
1. Run the `.exe` installer
2. Follow the setup wizard
3. Launch DutySlip from the Start menu

### 3. Start the app

1. Make sure **Docker Desktop is running**
2. Open the DutySlip control panel
3. Click **▶ Start Application**
4. Wait for the status to show **DutySlip is running** (green dot)
5. Your browser will open automatically at `http://localhost`

### 4. Stop the app

Click **■ Stop Application** in the control panel.

> **Note:** Closing the control panel window minimizes it to the system tray. Right-click the tray icon and select **Quit** to fully exit.

---

## Option B — Run via Docker (Developer Setup)

### 1. Clone the repository

```bash
git clone https://github.com/huzefa897/DutySlip.git
cd DutySlip
```

### 2. Create your `.env` file

```bash
cp .env.example .env
```

The default values in `.env.example` work out of the box for local development. Edit if needed:

```env
POSTGRES_DB=dutyslip
POSTGRES_USER=admin
POSTGRES_PASSWORD=secret
POSTGRES_HOST=db
POSTGRES_PORT=5432
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Build and start

```bash
docker compose up --build
```

First run takes 3–5 minutes (downloads base images, installs dependencies, builds frontend).

### 4. Access the app

Visit `http://localhost` in your browser.

### 5. Stop the app

```bash
docker compose down
```

---

## First-Time Setup (Both Options)

After starting the app for the first time:

1. Go to **⚙ Settings** in the navbar
2. Fill in your **Business Details** (name, ABN, address, phone, email)
3. Upload your **Logo**
4. Select your **Currency** ($ or ₹)
5. Click **Save Settings**

---

## Backup & Restore

### Export a backup

Go to **Settings → Backup & Restore → Download + Push**

This downloads a JSON file locally and (if configured) pushes to your GitHub backup repo.

### Restore from backup

**From a local file:**
Settings → Restore from Local File → Choose File → Restore

**From GitHub:**
Settings → Load GitHub Backups → select a backup → Restore

> ⚠️ Restoring replaces ALL existing data.

---

## GitHub Backup Setup (Optional)

To enable automatic cloud backups to a private GitHub repo:

1. Create a private GitHub repository (e.g. `dutyslip-backups`)
2. Generate a Personal Access Token with `repo` scope at `github.com → Settings → Developer Settings → Personal Access Tokens`
3. In the app go to **Settings → GitHub Backup**
4. Enter your GitHub username, repo name, and token
5. Click **Save GitHub Settings**

Every backup will now also push a versioned JSON file to your private repo.

---

## Updating to a New Version

### Electron App

1. Open the DutySlip control panel
2. Click **↑ Check for Updates**
3. If an update is available, click the download link
4. Install the new version — your data is stored in Docker volumes and is not affected

### Docker (Developer)

```bash
git pull
docker compose up --build
```

---

## Troubleshooting

### App won't start — "Docker not running"
Make sure Docker Desktop is open and the engine is running (check the Docker icon in your system tray/menu bar).

### App won't start — "Failed to start"
Try stopping first then starting again:
```bash
docker compose down
docker compose up --build
```

### Port 80 already in use
Another service is using port 80. Stop it or change the port in `docker-compose.yml`:
```yaml
ports:
  - "8080:80"   # change 80 to any free port
```
Then access the app at `http://localhost:8080`.

### Data lost after Docker volume wipe
Always export a backup before running `docker compose down -v`. The `-v` flag deletes volumes (your database).

### Logo not restored after backup
The logo image file is not included in the JSON backup. To fully backup including the logo, copy the `backend/media/` folder alongside your JSON file.

---

## Project Structure

```
DutySlip/
├── backend/          ← Django + DRF API
├── frontend/         ← Vue + Vite + Tailwind
├── electron/         ← Desktop control panel
├── docker-compose.yml
├── .env.example
└── .github/
    └── workflows/
        └── release.yml   ← Auto-builds .dmg + .exe on tag
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django, Django REST Framework |
| Frontend | Vue 3, Vite, Tailwind CSS |
| Database | PostgreSQL 15 |
| PDF Generation | WeasyPrint |
| Desktop App | Electron |
| Containerisation | Docker, Docker Compose |
| Web Server | Nginx |
| CI/CD | GitHub Actions |

---

## Release Process (Maintainer)

```bash
# 1. Bump version in electron/package.json
# 2. Commit changes
git add .
git commit -m "release: vX.X.X"

# 3. Tag and push
git tag vX.X.X
git push origin main --tags

# GitHub Actions automatically builds .dmg + .exe and creates a release
```

---

*Built by Huzefa Saleem*