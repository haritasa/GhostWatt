"""Validated, source-local Building 59 CSV ingestion and normalization."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.entities import EnergyReading, OccupancyReading, WeatherReading, WifiReading

BUILDING_ID = "building-59"
ENERGY_COLUMNS = ["mels_S", "lig_S", "mels_N", "hvac_N", "hvac_S"]
OCCUPANCY_COLUMNS = ["occ_third_south", "occ_fourth_south"]
WIFI_COLUMNS = ["wifi_first_south", "wifi_second_south", "wifi_third_south", "wifi_fourth_south"]
WEATHER_COLUMNS = ["air_temp_set_1", "relative_humidity_set_1", "solar_radiation_set_1"]


@dataclass(frozen=True)
class IngestionResult:
    energy_readings: int
    occupancy_intervals: int
    wifi_intervals: int
    weather_intervals: int


def _require_columns(frame: pd.DataFrame, expected: list[str], filename: str) -> None:
    missing = set(expected).difference(frame.columns)
    if missing:
        raise ValueError(f"{filename} is missing required columns: {', '.join(sorted(missing))}")


def _read_optional(source_dir: Path, filename: str) -> pd.DataFrame | None:
    path = source_dir / filename
    return pd.read_csv(path) if path.is_file() else None


def _insert(db: Session, model: type, rows: list[dict]) -> None:
    if rows:
        db.bulk_insert_mappings(model, rows)


def ingest_building_59(db: Session, source_dir: Path) -> IngestionResult:
    """Replace normalized Building 59 readings from a configured data directory.

    Timestamps stay source-local because the publication does not specify a zone.
    All sources are placed on 15-minute bins without forward-filling absent data.
    Wi-Fi is persisted only as a device-count proxy, never as people.
    """
    source_dir = source_dir.expanduser().resolve()
    energy_file = source_dir / "ele.csv"
    if not energy_file.is_file():
        raise ValueError("source_dir must contain ele.csv")

    energy = pd.read_csv(energy_file)
    _require_columns(energy, ["date", *ENERGY_COLUMNS], "ele.csv")
    energy = energy[["date", *ENERGY_COLUMNS]].copy()
    energy["timestamp"] = pd.to_datetime(energy.pop("date"), format="%Y/%m/%d %H:%M", errors="coerce").dt.floor("15min")
    energy[ENERGY_COLUMNS] = energy[ENERGY_COLUMNS].apply(pd.to_numeric, errors="coerce")
    # Average point power within malformed 5/10-minute source fragments into a canonical bin.
    energy = energy.dropna(subset=["timestamp"]).groupby("timestamp", as_index=False)[ENERGY_COLUMNS].mean()
    energy["total_kw"] = energy[ENERGY_COLUMNS].sum(axis=1, min_count=len(ENERGY_COLUMNS))
    energy = energy.dropna(subset=["total_kw"]).sort_values("timestamp")

    camera = _read_optional(source_dir, "occ.csv")
    if camera is not None:
        _require_columns(camera, ["date", *OCCUPANCY_COLUMNS], "occ.csv")
        camera = camera[["date", *OCCUPANCY_COLUMNS]].copy()
        camera["timestamp"] = pd.to_datetime(camera.pop("date"), format="%Y-%m-%d %H:%M:%S", errors="coerce")
        camera[OCCUPANCY_COLUMNS] = camera[OCCUPANCY_COLUMNS].apply(pd.to_numeric, errors="coerce")
        camera["occupancy_count"] = camera[OCCUPANCY_COLUMNS].sum(axis=1, min_count=len(OCCUPANCY_COLUMNS))
        camera = camera.dropna(subset=["timestamp", "occupancy_count"]).set_index("timestamp")["occupancy_count"].resample("15min").mean().dropna().reset_index()

    wifi = _read_optional(source_dir, "wifi.csv")
    if wifi is not None:
        _require_columns(wifi, ["date", *WIFI_COLUMNS], "wifi.csv")
        wifi = wifi[["date", *WIFI_COLUMNS]].copy()
        wifi["timestamp"] = pd.to_datetime(wifi.pop("date"), format="%Y/%m/%d %H:%M", errors="coerce")
        wifi[WIFI_COLUMNS] = wifi[WIFI_COLUMNS].apply(pd.to_numeric, errors="coerce")
        wifi["device_count"] = wifi[WIFI_COLUMNS].sum(axis=1, min_count=1)
        # DST duplicate local readings become one source-local 15-minute proxy observation.
        wifi = wifi.dropna(subset=["timestamp", "device_count"]).set_index("timestamp")["device_count"].resample("15min").mean().dropna().reset_index()

    weather = _read_optional(source_dir, "site_weather.csv")
    if weather is not None:
        _require_columns(weather, ["date", *WEATHER_COLUMNS], "site_weather.csv")
        weather = weather[["date", *WEATHER_COLUMNS]].copy()
        weather["timestamp"] = pd.to_datetime(weather.pop("date"), format="%Y-%m-%d %H:%M:%S", errors="coerce").dt.floor("15min")
        weather[WEATHER_COLUMNS] = weather[WEATHER_COLUMNS].apply(pd.to_numeric, errors="coerce")
        weather = weather.dropna(subset=["timestamp"]).groupby("timestamp", as_index=False)[WEATHER_COLUMNS].mean()

    db.execute(delete(EnergyReading).where(EnergyReading.building_id == BUILDING_ID))
    db.execute(delete(OccupancyReading).where(OccupancyReading.building_id == BUILDING_ID))
    db.execute(delete(WifiReading).where(WifiReading.building_id == BUILDING_ID))
    db.execute(delete(WeatherReading).where(WeatherReading.building_id == BUILDING_ID))
    _insert(db, EnergyReading, [{"building_id": BUILDING_ID, "timestamp": row.timestamp.to_pydatetime(), "total_kw": float(row.total_kw), "interval_minutes": 15.0, "source_file": "ele.csv", "quality_flag": "complete_component_total"} for row in energy[["timestamp", "total_kw"]].itertuples(index=False)])
    _insert(db, OccupancyReading, [] if camera is None else [{"building_id": BUILDING_ID, "timestamp": row.timestamp.to_pydatetime(), "occupancy_count": float(row.occupancy_count), "source_file": "occ.csv", "coverage_status": "observed_camera_people"} for row in camera.itertuples(index=False)])
    _insert(db, WifiReading, [] if wifi is None else [{"building_id": BUILDING_ID, "timestamp": row.timestamp.to_pydatetime(), "device_count": float(row.device_count), "source_file": "wifi.csv", "coverage_status": "observed_device_proxy"} for row in wifi.itertuples(index=False)])
    _insert(db, WeatherReading, [] if weather is None else [{"building_id": BUILDING_ID, "timestamp": row.timestamp.to_pydatetime(), "air_temp_c": None if pd.isna(row.air_temp_set_1) else float(row.air_temp_set_1), "relative_humidity": None if pd.isna(row.relative_humidity_set_1) else float(row.relative_humidity_set_1), "solar_radiation": None if pd.isna(row.solar_radiation_set_1) else float(row.solar_radiation_set_1), "source_file": "site_weather.csv"} for row in weather.itertuples(index=False)])
    db.commit()
    return IngestionResult(len(energy), 0 if camera is None else len(camera), 0 if wifi is None else len(wifi), 0 if weather is None else len(weather))


@dataclass(frozen=True)
class ClearResult:
    energy_readings: int
    occupancy_intervals: int
    wifi_intervals: int
    weather_intervals: int
    anomaly_events: int


def clear_building_59(db: Session) -> ClearResult:
    """Delete only Building 59's imported inputs and generated investigation data."""
    from app.models.entities import AnomalyEvent, AnomalyInterval

    event_ids = select(AnomalyEvent.id).where(AnomalyEvent.building_id == BUILDING_ID)
    event_count = db.query(AnomalyEvent).filter(AnomalyEvent.building_id == BUILDING_ID).count()
    energy_count = db.query(EnergyReading).filter(EnergyReading.building_id == BUILDING_ID).count()
    occupancy_count = db.query(OccupancyReading).filter(OccupancyReading.building_id == BUILDING_ID).count()
    wifi_count = db.query(WifiReading).filter(WifiReading.building_id == BUILDING_ID).count()
    weather_count = db.query(WeatherReading).filter(WeatherReading.building_id == BUILDING_ID).count()
    db.execute(delete(AnomalyInterval).where(AnomalyInterval.event_id.in_(event_ids)))
    db.execute(delete(AnomalyEvent).where(AnomalyEvent.building_id == BUILDING_ID))
    db.execute(delete(EnergyReading).where(EnergyReading.building_id == BUILDING_ID))
    db.execute(delete(OccupancyReading).where(OccupancyReading.building_id == BUILDING_ID))
    db.execute(delete(WifiReading).where(WifiReading.building_id == BUILDING_ID))
    db.execute(delete(WeatherReading).where(WeatherReading.building_id == BUILDING_ID))
    db.commit()
    return ClearResult(energy_count, occupancy_count, wifi_count, weather_count, event_count)
