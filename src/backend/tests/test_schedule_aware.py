"""Repeatable tests for the historical schedule-aware baseline and persistence."""

from datetime import datetime, timedelta

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # register ORM metadata
from app.core.config import DetectionPolicy
from app.db.database import Base
from app.ml.baseline_detector import ScheduleAwareBaselineModel
from app.models.entities import AnomalyEvent, EnergyReading
from app.services.anomaly_service import _occupancy_context, run_detection
from app.services.ingestion_service import clear_building_59


def test_policy_classifies_schedule_periods() -> None:
    policy = DetectionPolicy(holiday_dates=frozenset({datetime(2020, 7, 3).date()}))
    assert policy.is_low_occupancy_schedule(datetime(2020, 1, 6, 20))[0]  # Monday overnight
    assert policy.is_low_occupancy_schedule(datetime(2020, 1, 4, 12))[1] == "Weekend schedule"
    assert policy.is_low_occupancy_schedule(datetime(2020, 7, 3, 12))[1] == "Configured holiday schedule"
    assert not policy.is_low_occupancy_schedule(datetime(2020, 1, 6, 12))[0]


def test_baseline_uses_only_prior_comparable_history() -> None:
    timestamps = pd.to_datetime(["2020-01-06 20:00", "2020-01-13 20:00", "2020-01-20 20:00"])
    readings = pd.DataFrame({"timestamp": timestamps, "actual_kwh": [10.0, 20.0, 100.0]})
    policy = DetectionPolicy(minimum_comparable_samples=2)
    scored = ScheduleAwareBaselineModel().fit(readings, policy).score()
    assert pd.isna(scored.iloc[0].expected_kwh)
    assert scored.iloc[2].baseline_support == 2
    assert scored.iloc[2].expected_kwh == 15.0  # median(10, 20), never includes 100


def test_detection_works_without_camera_occupancy(tmp_path, monkeypatch) -> None:
    # The model must rely on schedule context when direct camera coverage is absent.
    db_url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    from app.services import anomaly_service

    monkeypatch.setattr(anomaly_service.settings, "DETECTION_POLICY", DetectionPolicy(minimum_comparable_samples=4))
    start = datetime(2020, 1, 6, 20)
    for index in range(5):
        session.add(EnergyReading(building_id="building-59", timestamp=start + timedelta(days=index * 7), total_kw=4.0 if index < 4 else 20.0, interval_minutes=15.0, source_file="fixture"))
    session.commit()
    assert run_detection(session, "building-59") == 1
    event = session.query(AnomalyEvent).filter_by(building_id="building-59", is_current=True).one()
    assert event.title == "Off-hours excess energy use"
    assert event.occupancy_value == 0.0  # Legacy SQLite schema is non-null; API maps unavailable to null.
    assert _occupancy_context(event)["value"] is None
    cleared = clear_building_59(session)
    assert cleared.energy_readings == 5 and cleared.anomaly_events == 1
    assert session.query(EnergyReading).filter_by(building_id="building-59").count() == 0
    assert session.query(AnomalyEvent).filter_by(building_id="building-59").count() == 0
