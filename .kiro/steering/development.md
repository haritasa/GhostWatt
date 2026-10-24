# GhostWatt development workflow

## Architecture

- FastAPI backend: `src/backend/app/`
- React/Vite frontend: `src/frontend/`
- Local SQLite database: `src/backend/ghostwatt.db` (never commit it)
- Backend tests: `src/backend/tests/`

## Implementation standards

- Use Pydantic response models for public API fields.
- Keep SQLite operations scoped by `building_id`; never delete records for other buildings while recalculating one building.
- Make data-clearing operations explicit and confirmed in the UI.
- When a data source is unavailable, expose that fact in API/UI evidence rather than treating it as zero.
- Validate changed backend behavior with `../../.venv/bin/python -m pytest tests -q` from `src/backend`.
- Validate frontend changes with `npm run build` from `src/frontend`.

## Submission safety

Do not commit `ghostwatt.db`, personal filesystem paths, secrets, or the 2.4 GB local source dataset. Keep reproducible import instructions in `README.md` and use a documented source location or an approved Git LFS/data-release strategy for distribution.
