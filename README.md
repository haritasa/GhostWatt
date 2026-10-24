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

Open http://localhost:5173. The dashboard uses the stable `/api/dashboard`, `/api/anomalies`, and `/api/anomalies/{event_id}` contracts.

### Load and analyze Building 59

The app deliberately does not auto-ingest a multi-gigabyte dataset. In the dashboard's **Demo view**, paste the absolute path to the folder containing `ele.csv` and `occ.csv` and select **Import & analyze**. You can instead copy that folder to `data/raw/Building_59/Bldg59_clean data`, or set `BUILDING_59_DATA_DIR` before starting FastAPI.

`ele.csv` is normalized as five kW signals; interval kWh is calculated using each observed duration. One-minute occupancy counts are averaged into 15-minute intervals. The detector compares each low-occupancy interval against the median of the same hour, weekday/weekend category, and occupancy category. Thresholds, event-gap tolerance, cost rate, and CO₂ rate are all configurable through environment variables defined in `src/backend/app/core/config.py`.
Add shadcn components with `npx shadcn@latest add button`.

### Schedule-aware anomaly model

The current detector is `schedule-aware-median-v1`. It only evaluates configured low-occupancy schedule periods: overnight (19:00–07:00 source-local time by default), weekends, and optional `HOLIDAY_DATES` (`YYYY-MM-DD` comma-separated). It predicts expected kWh from the **median of prior** comparable 15-minute intervals, first matching quarter-hour + weekday/weekend + season, then using documented coarser fallbacks when necessary. An event requires both material kWh excess and percentage deviation.

Camera occupancy remains a direct people count where it is available. `wifi.csv` is imported separately as a device-count proxy and is never represented as people or substituted for camera occupancy. `site_weather.csv` is normalized and retained for phase-two modeling; the MVP baseline does not yet use it as a predictive feature. All displayed timestamps are source-local because the published dataset does not specify a timezone. Results are investigation candidates, not verified waste or savings.

Policy environment variables include `OVERNIGHT_START_HOUR`, `OVERNIGHT_END_HOUR`, `WEEKENDS_ARE_LOW_OCCUPANCY`, `HOLIDAY_DATES`, `MINIMUM_EXCESS_KWH`, `MINIMUM_DEVIATION_PERCENT`, `MINIMUM_COMPARABLE_SAMPLES`, `EVENT_GAP_TOLERANCE_MINUTES`, `ELECTRICITY_COST_PER_KWH`, and `CO2_KG_PER_KWH`.

### Test the backend

```bash
cd src/backend
../../.venv/bin/python -m pytest tests -q
```

Tests use a temporary SQLite database and never connect to `ghostwatt.db`.

### Hackathon submission materials

- [Submission description, testing guide, and Kiro usage write-up](docs/hackathon-submission.md)
- [Under-three-minute demonstration video script](docs/demo-video-script.md)
- [Committed Kiro steering and hook configuration](.kiro/)

The `.kiro/` directory is intentionally committed for the hackathon submission. It contains project steering and a post-spec-task backend test hook; it must not be added to `.gitignore`.
