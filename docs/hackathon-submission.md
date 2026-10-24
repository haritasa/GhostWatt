# GhostWatt — Hackathon Submission Material

## Challenge track

**Climate Tech & Clean Energy**

## Team members — maximum four

Replace these placeholders before submitting:

1. `Ayman Blanco`
2. ``


## Public repository

https://github.com/haritasa/GhostWatt

## Project description

GhostWatt is an AI-powered building energy-auditing platform for commercial building owners, property managers, facility teams, universities, and energy consultants. It helps teams identify potential avoidable electricity consumption using the meter and operational data they already collect.

The platform imports Building 59 electricity, camera occupancy, Wi-Fi device-proxy, and weather data into SQLite. It derives a total electricity signal from available component meters, then runs an explainable schedule-aware baseline model. For each 15-minute interval, GhostWatt compares actual energy use with the median of prior comparable periods. It focuses investigation on overnight, weekend, and configured-holiday periods where electricity is materially above the historical expected level.

The React dashboard translates those candidates into actionable operations information: ranked events, actual-versus-expected interval evidence, schedule and occupancy context, estimated cost and carbon impact, recommended next steps, and investigation status controls. GhostWatt is designed to make energy auditing more accessible for buildings without expensive building-management analytics systems.

## Core functionality

- **Energy dashboard:** total energy, potential excess use, estimated cost opportunity, estimated CO₂ impact, and event counts.
- **Explainable anomaly detection:** a historical, schedule-aware median baseline that only uses prior comparable intervals.
- **Operational context:** camera people counts where available, separately labeled Wi-Fi device-count proxy data, schedule context, source-quality labels, and weather retained for future model enrichment.
- **Action workflow:** event details, recommendations, and persisted `new`, `investigating`, `resolved`, or `dismissed` statuses.
- **Safe data reset:** a confirmed UI action clears Building 59's persisted source readings and events before a fresh import.

## Run and test

See `README.md` for the complete local setup. In short:

```bash
# Terminal 1 — backend
cd src/backend
../../.venv/bin/python -m uvicorn app.main:app --reload

# Terminal 2 — frontend
cd src/frontend
npm install
npm run dev
```

Use the dashboard **Import** button to select the local folder containing `ele.csv`, `occ.csv`, `wifi.csv`, and `site_weather.csv`. The supplied full Building 59 source folder is large, so it is intentionally not committed to ordinary Git; configure its local path at import time or provide an approved release/LFS distribution before judging.

Run backend tests:

```bash
cd src/backend
../../.venv/bin/python -m pytest tests -q
```

Run the frontend production build:

```bash
cd src/frontend
npm run build
```

## Demonstration video

Record a public video under three minutes using the script in `docs/demo-video-script.md`. It must visibly show GhostWatt functioning in a browser and be uploaded publicly to an approved video platform before its URL is submitted.

## How Kiro was used

This project was developed in **Kiro IDE** using an iterative conversational/Vibe workflow.

### Kiro IDE and agent tools

Kiro was used to inspect the existing FastAPI/React project, analyze the local Building 59 file schema, plan architecture, create and edit backend/frontend code, generate documentation, and run validation commands. Kiro's repository-aware reading, search, terminal, and file-editing tools helped trace the flow from CSV ingestion through SQLite, API contracts, and React views.

Kiro's context-gathering agent was used before major changes to map the existing codebase and dataset details, including power units, timestamp formats, coverage gaps, camera occupancy limitations, Wi-Fi proxy behavior, and weather coverage. This kept the implementation grounded in the actual delivered CSV fields instead of assumed schemas.

### Planning compared with vibe coding

The work began conversationally to explore the product and existing code, then used a detailed schedule-aware anomaly-model task breakdown to guide implementation. The structured plan made dependencies explicit: normalize source data first, preserve provenance, build a historical-only baseline, persist evidence, keep API contracts stable, and validate behavior. This was more controlled than making isolated UI or detector changes without considering data semantics and persistence.

### Steering

The committed `.kiro/steering/` files provide project-level guidance for future Kiro sessions. They capture GhostWatt's data semantics, API compatibility requirements, validation commands, and submission safeguards. This reduces repeated context gathering and helps prevent mistakes such as treating Wi-Fi device counts as people or displaying a candidate as verified savings.

### Agent hook

The committed `.kiro/hooks/run-backend-tests.json` hook runs the backend test suite after a Kiro spec task completes. It provides a repeatable verification step when structured Kiro tasks are used. The hook is intentionally portable, non-destructive, and contains no credentials.

### Capabilities not claimed

This submission does **not** claim use of Kiro CLI, Kiro Web, Crew, MCP integrations, property-based testing, or Kiro Powers. Those tools were not required for the implemented workflow, so they are not represented as used.

## Original-work and data note

GhostWatt application code and presentation material should be reviewed by the team before submission to ensure the team owns or has permission to use every included asset. The Building 59 dataset is treated as an external research dataset; retain its required attribution, license, and distribution terms when sharing it.
