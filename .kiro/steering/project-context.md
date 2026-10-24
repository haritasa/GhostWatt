# GhostWatt project context

GhostWatt is a Climate Tech & Clean Energy project that helps commercial-building operators investigate potential energy waste from historical data.

## Product rules

- Present detected items as **investigation candidates**, not verified waste or guaranteed savings.
- Keep the frontend display-only for energy analysis: detection, thresholds, baseline values, cost, and CO₂ calculations belong in the backend.
- Preserve the distinction between data types: camera occupancy is a people count; Wi-Fi is only a device-count proxy; electricity source fields are power in kW and must be converted to kWh using interval duration.
- Source timestamps are source-local because the Building 59 dataset does not provide an authoritative timezone.

## Current approach

The MVP uses `schedule-aware-median-v1`, an explainable baseline rather than a black-box model. It compares each low-occupancy schedule interval with prior comparable 15-minute readings using calendar context and a median baseline. Events require both material excess kWh and percentage deviation.

## Public API compatibility

Maintain these endpoints unless an explicit migration is requested:

- `POST` and `DELETE` `/api/ingestion/building-59`
- `POST` `/api/detection/building-59`
- `GET` `/api/dashboard`
- `GET` `/api/anomalies`
- `GET` and `PATCH` `/api/anomalies/{event_id}`
