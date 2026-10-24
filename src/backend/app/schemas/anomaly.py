"""Stable, UI-ready anomaly API response models."""

from typing import Literal
from pydantic import BaseModel, Field

EventStatus = Literal["new", "investigating", "resolved", "dismissed"]
Severity = Literal["low", "medium", "high", "critical"]

class OccupancyContext(BaseModel):
    label: str
    value: float | None
    unit: str = "people"

class EnergyEvidence(BaseModel):
    actual_kwh: float
    expected_kwh: float
    excess_kwh: float
    deviation_percent: float

class Impact(BaseModel):
    estimated_cost_usd: float
    estimated_co2_kg: float

class AnomalyEventSummary(BaseModel):
    id: str
    title: str
    status: EventStatus
    severity: Severity
    start_at: str
    end_at: str
    duration_minutes: int
    occupancy_context: OccupancyContext
    energy: EnergyEvidence
    impact: Impact
    confidence: Literal["low", "medium", "high"]
    recommended_action: str
    schedule_context: str | None = None
    baseline_version: str | None = None
    policy_version: str | None = None
    data_quality_summary: str | None = None

class AnomalyListResponse(BaseModel):
    items: list[AnomalyEventSummary]
    total: int

class Explanation(BaseModel):
    headline: str
    actual_kwh: float
    expected_kwh: float
    excess_kwh: float
    baseline_method: str
    comparison_context: list[str]

class DetailedImpact(Impact):
    assumptions: list[str]

class RecommendedAction(BaseModel):
    title: str
    reason: str

class IntervalEvidence(BaseModel):
    timestamp: str
    actual_kwh: float
    expected_kwh: float
    occupancy_value: float | None
    occupancy_unit: str
    occupancy_source: str | None = None
    schedule_context: str | None = None
    baseline_support: int | None = None
    data_quality: str | None = None
    is_anomalous: bool

class AnomalyEventDetail(AnomalyEventSummary):
    explanation: Explanation
    impact: DetailedImpact
    recommended_actions: list[RecommendedAction]
    intervals: list[IntervalEvidence]

class UpdateEventStatusRequest(BaseModel):
    status: EventStatus

class IngestionRequest(BaseModel):
    source_dir: str | None = Field(default=None, description="Optional override; default is BUILDING_59_DATA_DIR.")

class IngestionResponse(BaseModel):
    building_id: str
    energy_readings: int
    occupancy_intervals: int
    wifi_intervals: int = 0
    weather_intervals: int = 0
    anomaly_events: int
    source_dir: str

class DetectionResponse(BaseModel):
    building_id: str
    anomaly_events: int
    policy_version: str
    baseline_version: str
    message: str


class ClearDataResponse(BaseModel):
    building_id: str
    energy_readings_deleted: int
    occupancy_intervals_deleted: int
    wifi_intervals_deleted: int
    weather_intervals_deleted: int
    anomaly_events_deleted: int
    message: str
