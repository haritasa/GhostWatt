"""Schedule-aware scoring, event persistence, and UI-ready projections."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha1

import pandas as pd
from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.ml.baseline_detector import BASELINE_METHOD, ScheduleAwareBaselineModel
from app.models.entities import AnomalyEvent, AnomalyInterval, EnergyReading, OccupancyReading, WeatherReading, WifiReading

BUILDING_NAME = "Berkeley Building 59"
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
RECOMMENDED_ACTION = "Review HVAC, lighting, and equipment schedules."


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="minutes")


def _round(value: float | None) -> float | None:
    return None if value is None else round(float(value), 2)


def _severity(excess_kwh: float, deviation_percent: float) -> str:
    if excess_kwh >= 20 or deviation_percent >= 200: return "critical"
    if excess_kwh >= 8 or deviation_percent >= 100: return "high"
    if excess_kwh >= 3 or deviation_percent >= 60: return "medium"
    return "low"


def _confidence(support: int) -> str:
    if support >= 30: return "high"
    if support >= 15: return "medium"
    return "low"


def _analysis_frame(db: Session, building_id: str) -> pd.DataFrame:
    energy = pd.DataFrame(db.execute(select(EnergyReading.timestamp, EnergyReading.total_kw, EnergyReading.interval_minutes).where(EnergyReading.building_id == building_id)).all(), columns=["timestamp", "total_kw", "interval_minutes"])
    if energy.empty: return energy
    camera = pd.DataFrame(db.execute(select(OccupancyReading.timestamp, OccupancyReading.occupancy_count).where(OccupancyReading.building_id == building_id)).all(), columns=["timestamp", "camera_people"])
    wifi = pd.DataFrame(db.execute(select(WifiReading.timestamp, WifiReading.device_count).where(WifiReading.building_id == building_id)).all(), columns=["timestamp", "wifi_device_count"])
    weather = pd.DataFrame(db.execute(select(WeatherReading.timestamp, WeatherReading.air_temp_c).where(WeatherReading.building_id == building_id)).all(), columns=["timestamp", "air_temp_c"])
    frame = energy.merge(camera, on="timestamp", how="left").merge(wifi, on="timestamp", how="left").merge(weather, on="timestamp", how="left")
    frame = frame[(frame.interval_minutes > 0) & (frame.interval_minutes <= 30)].copy()
    frame["actual_kwh"] = frame.total_kw * frame.interval_minutes / 60
    schedule = frame.timestamp.map(settings.DETECTION_POLICY.is_low_occupancy_schedule)
    frame["is_low_schedule"] = schedule.map(lambda item: item[0])
    frame["schedule_context"] = schedule.map(lambda item: item[1])
    frame["occupancy_source"] = "unavailable"
    frame.loc[frame.wifi_device_count.notna(), "occupancy_source"] = "wifi_device_proxy"
    frame.loc[frame.camera_people.notna(), "occupancy_source"] = "camera_people"
    frame["data_quality"] = frame.occupancy_source.map(lambda source: "complete_component_total; " + source)
    return frame.sort_values("timestamp")


def run_detection(db: Session, building_id: str = "building-59") -> int:
    """Score schedule-defined low-occupancy intervals from historical evidence only."""
    policy = settings.DETECTION_POLICY
    readings = _analysis_frame(db, building_id)
    if readings.empty: return 0
    scored = ScheduleAwareBaselineModel().fit(readings, policy).score()
    scored["excess_kwh"] = scored.actual_kwh - scored.expected_kwh
    scored["deviation_percent"] = scored.excess_kwh.div(scored.expected_kwh).mul(100)
    candidates = scored[
        scored.is_low_schedule
        & (scored.baseline_support >= policy.minimum_comparable_samples)
        & (scored.expected_kwh > policy.near_zero_expected_kwh)
        & (scored.excess_kwh >= policy.minimum_excess_kwh)
        & (scored.deviation_percent >= policy.minimum_deviation_percent)
    ].sort_values("timestamp")

    db.execute(update(AnomalyEvent).where(AnomalyEvent.building_id == building_id).values(is_current=False))
    existing = {event.fingerprint: event for event in db.scalars(select(AnomalyEvent).where(AnomalyEvent.building_id == building_id)).all()}
    building_event_ids = select(AnomalyEvent.id).where(AnomalyEvent.building_id == building_id)
    db.execute(delete(AnomalyInterval).where(AnomalyInterval.event_id.in_(building_event_ids)))

    groups: list[list[object]] = []; current: list[object] = []; previous_end: pd.Timestamp | None = None
    for row in candidates.itertuples(index=False):
        interval_end = row.timestamp + pd.Timedelta(minutes=float(row.interval_minutes))
        if previous_end is not None and row.timestamp - previous_end > pd.Timedelta(minutes=policy.event_gap_tolerance_minutes):
            groups.append(current); current = []
        current.append(row); previous_end = interval_end
    if current: groups.append(current)

    for rows in groups:
        event_frame = pd.DataFrame(rows)
        start_at = event_frame.timestamp.min().to_pydatetime()
        end_at = (event_frame.timestamp + pd.to_timedelta(event_frame.interval_minutes, unit="min")).max().to_pydatetime()
        actual_kwh, expected_kwh = float(event_frame.actual_kwh.sum()), float(event_frame.expected_kwh.sum())
        excess_kwh = actual_kwh - expected_kwh
        deviation_percent = excess_kwh / expected_kwh * 100 if expected_kwh else 0.0
        fingerprint = sha1(f"{building_id}:{policy.version}:{start_at.isoformat()}:{end_at.isoformat()}".encode()).hexdigest()
        event = existing.get(fingerprint)
        camera_values = event_frame.camera_people.dropna()
        values = {
            "public_id": f"event-{start_at:%Y%m%d-%H%M}-{fingerprint[:6]}", "building_id": building_id, "fingerprint": fingerprint,
            "title": "Off-hours excess energy use", "severity": _severity(excess_kwh, deviation_percent), "start_at": start_at, "end_at": end_at,
            "duration_minutes": max(1, round((end_at - start_at).total_seconds() / 60)), "occupancy_value": 0.0 if camera_values.empty else float(camera_values.mean()),
            "actual_kwh": actual_kwh, "expected_kwh": expected_kwh, "excess_kwh": excess_kwh, "deviation_percent": deviation_percent,
            "estimated_cost_usd": excess_kwh * policy.electricity_cost_per_kwh, "estimated_co2_kg": excess_kwh * policy.co2_kg_per_kwh,
            "confidence": _confidence(int(event_frame.baseline_support.min())), "baseline_method": BASELINE_METHOD,
            "baseline_version": ScheduleAwareBaselineModel.version, "policy_version": policy.version,
            "schedule_context": event_frame.schedule_context.iloc[0], "data_quality_summary": "; ".join(sorted(event_frame.data_quality.unique())), "is_current": True,
        }
        if event is None:
            event = AnomalyEvent(status="new", **values); db.add(event); db.flush()
        else:
            for key, value in values.items(): setattr(event, key, value)
            db.flush()
        db.add_all([AnomalyInterval(event_id=event.id, timestamp=row.timestamp.to_pydatetime(), interval_minutes=float(row.interval_minutes), actual_kwh=float(row.actual_kwh), expected_kwh=float(row.expected_kwh), occupancy_value=0.0 if pd.isna(row.camera_people) else float(row.camera_people), occupancy_source=row.occupancy_source, schedule_context=row.schedule_context, baseline_support=int(row.baseline_support), data_quality=row.data_quality) for row in rows])
    db.commit()
    return len(groups)


def _occupancy_context(event: AnomalyEvent) -> dict:
    if "camera_people" not in (event.data_quality_summary or ""):
        return {"label": f"{event.schedule_context or 'Off-hours'}; no camera occupancy coverage", "value": None, "unit": "people"}
    return {"label": f"{event.schedule_context or 'Off-hours'}; observed camera occupancy", "value": _round(event.occupancy_value), "unit": "people"}


def _summary(event: AnomalyEvent) -> dict:
    return {"id": event.public_id, "title": event.title, "status": event.status, "severity": event.severity, "start_at": _iso(event.start_at), "end_at": _iso(event.end_at), "duration_minutes": event.duration_minutes, "occupancy_context": _occupancy_context(event), "energy": {"actual_kwh": _round(event.actual_kwh), "expected_kwh": _round(event.expected_kwh), "excess_kwh": _round(event.excess_kwh), "deviation_percent": _round(event.deviation_percent)}, "impact": {"estimated_cost_usd": _round(event.estimated_cost_usd), "estimated_co2_kg": _round(event.estimated_co2_kg)}, "confidence": event.confidence, "recommended_action": RECOMMENDED_ACTION, "schedule_context": event.schedule_context, "baseline_version": event.baseline_version, "policy_version": event.policy_version, "data_quality_summary": event.data_quality_summary}


def list_events(db: Session, building_id: str, status: str | None = None, limit: int = 20) -> list[AnomalyEvent]:
    statement = select(AnomalyEvent).where(AnomalyEvent.building_id == building_id, AnomalyEvent.is_current.is_(True))
    if status: statement = statement.where(AnomalyEvent.status == status)
    return list(db.scalars(statement.order_by(AnomalyEvent.start_at.desc()).limit(limit)).all())


def list_event_summaries(db: Session, building_id: str, status: str | None, limit: int) -> list[dict]: return [_summary(event) for event in list_events(db, building_id, status, limit)]

def get_event_detail(db: Session, public_id: str) -> AnomalyEvent | None:
    return db.scalar(select(AnomalyEvent).options(selectinload(AnomalyEvent.intervals)).where(AnomalyEvent.public_id == public_id, AnomalyEvent.is_current.is_(True)))

def event_detail(event: AnomalyEvent) -> dict:
    payload = _summary(event)
    payload.update({"explanation": {"headline": f"Electricity use was {event.deviation_percent:.0f}% above the historical expected level during {event.schedule_context or 'a low-occupancy schedule'}.", "actual_kwh": _round(event.actual_kwh), "expected_kwh": _round(event.expected_kwh), "excess_kwh": _round(event.excess_kwh), "baseline_method": event.baseline_method, "comparison_context": ["Same 15-minute schedule slot", "Same weekday/weekend type", "Same season", event.schedule_context or "Schedule-defined off-hours"]}, "impact": {**payload["impact"], "assumptions": ["Estimated using configured electricity cost and CO₂ rates.", "Potential impact is not verified savings."]}, "recommended_actions": [{"title": "Review HVAC scheduling", "reason": "Off-hours load may indicate HVAC operation outside occupied hours."}, {"title": "Inspect lighting and plug-load controls", "reason": "Schedule-defined low occupancy should correspond to reduced non-essential load."}], "intervals": [{"timestamp": _iso(interval.timestamp), "actual_kwh": _round(interval.actual_kwh), "expected_kwh": _round(interval.expected_kwh), "occupancy_value": _round(interval.occupancy_value) if interval.occupancy_source == "camera_people" else None, "occupancy_unit": interval.occupancy_unit, "occupancy_source": interval.occupancy_source, "schedule_context": interval.schedule_context, "baseline_support": interval.baseline_support, "data_quality": interval.data_quality, "is_anomalous": interval.is_anomalous} for interval in event.intervals]})
    return payload

def dashboard(db: Session, building_id: str, start: datetime | None, end: datetime | None) -> dict:
    energy_filter = [EnergyReading.building_id == building_id, EnergyReading.interval_minutes <= 30]
    if start: energy_filter.append(EnergyReading.timestamp >= start)
    if end: energy_filter.append(EnergyReading.timestamp <= end)
    total_energy = db.scalar(select(func.coalesce(func.sum(EnergyReading.total_kw * EnergyReading.interval_minutes / 60), 0)).where(*energy_filter))
    event_filter = [AnomalyEvent.building_id == building_id, AnomalyEvent.is_current.is_(True)]
    if start: event_filter.append(AnomalyEvent.end_at >= start)
    if end: event_filter.append(AnomalyEvent.start_at <= end)
    events = list(db.scalars(select(AnomalyEvent).where(*event_filter)).all()); top_events = sorted(events, key=lambda event: (SEVERITY_ORDER[event.severity], -event.excess_kwh))[:5]
    return {"building": {"id": building_id, "name": BUILDING_NAME}, "period": {"start": _iso(start) if start else None, "end": _iso(end) if end else None}, "summary": {"total_energy_kwh": _round(total_energy), "anomalous_excess_kwh": _round(sum(event.excess_kwh for event in events)), "estimated_cost_impact_usd": _round(sum(event.estimated_cost_usd for event in events)), "estimated_co2_kg": _round(sum(event.estimated_co2_kg for event in events)), "anomaly_event_count": len(events)}, "top_events": [_summary(event) for event in top_events]}
