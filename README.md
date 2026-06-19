# GIS-HMS

GIS-based child malnutrition monitoring system for Cabadbaran City.

## Stack

- Frontend: Next.js 14 App Router, TypeScript, Tailwind, React Query, Zustand, Leaflet, Recharts
- Backend: FastAPI, SQLAlchemy async ORM, JWT auth
- Database: PostgreSQL database `HMS` with user `GIS`

## Local Setup

```powershell
# Backend
cd C:\Users\Ken\Documents\GIS-HMS
.\.venv\Scripts\pip.exe install -r backend\requirements.txt
cd backend
..\.venv\Scripts\python.exe -m app.scripts.seed
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Frontend
cd C:\Users\Ken\Documents\GIS-HMS\frontend
npm.cmd install
npm.cmd run dev -- -p 3000
```

Open `http://127.0.0.1:3000/login`.

Default accounts:

- Super Admin: `superadmin` / `Admin@123`
- Barangay admins: `admin_brgy1` through `admin_brgy15` / `Admin@123`

## Database

The backend uses:

```env
DATABASE_URL=postgresql+asyncpg://GIS:admin123@localhost:5432/HMS
```

This machine's PostgreSQL server does not currently have the PostGIS extension installed, so geometries are stored as GeoJSON `JSONB` for a runnable local build. The API still returns GeoJSON for map layers. After installing PostGIS, the geometry fields can be migrated back to native `Geometry(...)` columns.

## Verification

Completed checks:

```powershell
cd frontend
npm.cmd run typecheck
npm.cmd run build

cd ..
Invoke-RestMethod http://127.0.0.1:8000/api/health
```
