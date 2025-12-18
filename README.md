# MLR Modernized Stack

This repository now provides a FastAPI backend with SQLAlchemy models and a React (Vite) frontend that mirrors the existing Dash routes.

## Prerequisites
- Docker and Docker Compose
- Python 3.11+ / Node 20+ (for local development without containers)

## Environment
Copy `.env.example` to `.env` and adjust values. The backend reads `DATABASE_URL` and optional PI Web API credentials. The frontend uses `VITE_API_BASE_URL`.

```bash
cp .env.example .env
```

## Running with Docker Compose

```bash
docker-compose up --build
```

Services:
- **db**: Postgres
- **backend**: FastAPI on http://localhost:8000
- **frontend**: static app on http://localhost:4173

Run Alembic migrations inside the backend container if needed:

```bash
docker-compose exec backend alembic upgrade head
```

## Backend Development

Create a virtual environment, install dependencies, and start the API:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Tests

```bash
cd backend
pytest
```

## Frontend Development

Install dependencies and start Vite:

```bash
cd frontend
npm install
npm run dev
```

The frontend recreates the Dash routes (`/`, `/dashboard`, `/dados`, `/treinamento`, and modal pages) with Plotly visualizations and forms pointing at the FastAPI endpoints.
