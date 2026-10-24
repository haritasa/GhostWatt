"""Application settings and validated schedule-aware detection policy."""

import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parents[1]


def _csv_dates(value: str) -> frozenset[date]:
    if not value.strip():
        return frozenset()
    try:
        return frozenset(date.fromisoformat(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as error:
        raise ValueError("HOLIDAY_DATES must be comma-separated YYYY-MM-DD values") from error


@dataclass(frozen=True)
class DetectionPolicy:
    """Backend-owned schedule, threshold, and impact assumptions."""

    version: str = "schedule-aware-median-v1"
    overnight_start_hour: int = 19
    overnight_end_hour: int = 7
    weekends_are_low_occupancy: bool = True
    holiday_dates: frozenset[date] = field(default_factory=frozenset)
    minimum_excess_kwh: float = 0.50
    minimum_deviation_percent: float = 40.0
    minimum_comparable_samples: int = 8
    event_gap_tolerance_minutes: int = 30
    electricity_cost_per_kwh: float = 0.20
    co2_kg_per_kwh: float = 0.375
    near_zero_expected_kwh: float = 0.05

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError("DETECTION_POLICY_VERSION cannot be empty")
        if not 0 <= self.overnight_start_hour <= 23 or not 0 <= self.overnight_end_hour <= 23:
            raise ValueError("Overnight hours must be between 0 and 23")
        if self.overnight_start_hour == self.overnight_end_hour:
            raise ValueError("Overnight start and end hours must differ")
        if self.minimum_excess_kwh < 0 or self.minimum_deviation_percent < 0:
            raise ValueError("Anomaly thresholds cannot be negative")
        if self.minimum_comparable_samples < 2 or self.event_gap_tolerance_minutes < 0:
            raise ValueError("Minimum reference samples must be >= 2 and event gap must be non-negative")
        if self.electricity_cost_per_kwh < 0 or self.co2_kg_per_kwh < 0 or self.near_zero_expected_kwh <= 0:
            raise ValueError("Impact rates must be non-negative and near-zero expected kWh must be positive")

    def is_low_occupancy_schedule(self, timestamp: object) -> tuple[bool, str]:
        timestamp_date = timestamp.date()
        hour = timestamp.hour
        overnight = hour >= self.overnight_start_hour or hour < self.overnight_end_hour
        if timestamp_date in self.holiday_dates:
            return True, "Configured holiday schedule"
        if self.weekends_are_low_occupancy and timestamp.weekday() >= 5:
            return True, "Weekend schedule"
        if overnight:
            return True, "Overnight schedule"
        return False, "Scheduled occupied period"


class Settings:
    APP_NAME: str = "GhostWatt API"
    VERSION: str = "0.3.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'ghostwatt.db'}")
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    BUILDING_59_DATA_DIR: Path = Path(os.getenv("BUILDING_59_DATA_DIR", PROJECT_DIR / "data/raw/Building_59/Bldg59_clean data"))
    DETECTION_POLICY = DetectionPolicy(
        version=os.getenv("DETECTION_POLICY_VERSION", "schedule-aware-median-v1"),
        overnight_start_hour=int(os.getenv("OVERNIGHT_START_HOUR", "19")),
        overnight_end_hour=int(os.getenv("OVERNIGHT_END_HOUR", "7")),
        weekends_are_low_occupancy=os.getenv("WEEKENDS_ARE_LOW_OCCUPANCY", "true").lower() in {"1", "true", "yes"},
        holiday_dates=_csv_dates(os.getenv("HOLIDAY_DATES", "")),
        minimum_excess_kwh=float(os.getenv("MINIMUM_EXCESS_KWH", "0.50")),
        minimum_deviation_percent=float(os.getenv("MINIMUM_DEVIATION_PERCENT", "40")),
        minimum_comparable_samples=int(os.getenv("MINIMUM_COMPARABLE_SAMPLES", "8")),
        event_gap_tolerance_minutes=int(os.getenv("EVENT_GAP_TOLERANCE_MINUTES", "30")),
        electricity_cost_per_kwh=float(os.getenv("ELECTRICITY_COST_PER_KWH", "0.20")),
        co2_kg_per_kwh=float(os.getenv("CO2_KG_PER_KWH", "0.375")),
        near_zero_expected_kwh=float(os.getenv("NEAR_ZERO_EXPECTED_KWH", "0.05")),
    )


settings = Settings()
