## GhostWatt

AI-powered building energy waste detection.

### Structure

```
requirements.txt        # Python deps (backend + ML)
data/raw, data/processed  # datasets (git-ignored)
src/backend/app/        # FastAPI app
  main.py               # entry point
  api/                  # routes
  core/                 # config
  db/                   # SQLAlchemy + SQLite
  models/ schemas/      # ORM models / Pydantic schemas
  services/ ml/         # business logic / ML
src/frontend/           # React + Vite + Tailwind + shadcn
```

### Run the backend (port 8000)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd src/backend && uvicorn app.main:app --reload
```

macOS: XGBoost needs the OpenMP runtime (`brew install libomp`).

### Run the frontend (port 5173)

```bash
cd src/frontend
npm install
npm run dev
```

Open http://localhost:5173. It shows the hello-world message from `GET /api/hello`.
Add shadcn components with `npx shadcn@latest add button`.
