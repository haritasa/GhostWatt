"""Dashboard API response models."""

from pydantic import BaseModel

from app.schemas.anomaly import AnomalyEventSummary


class Building(BaseModel):
    id: str
    name: str


class Period(BaseModel):
    start: str | None
    end: str | None
    time_basis: str = "source local time (timezone not supplied by dataset)"


class DashboardSummary(BaseModel):
    total_energy_kwh: float
    anomalous_excess_kwh: float
    estimated_cost_impact_usd: float
    estimated_co2_kg: float
    anomaly_event_count: int


class DashboardResponse(BaseModel):
    building: Building
    period: Period
    summary: DashboardSummary
    top_events: list[AnomalyEventSummary]
