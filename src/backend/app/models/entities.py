"""SQLite persistence for normalized sources and reproducible anomaly evidence."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class EnergyReading(Base):
    __tablename__ = "energy_readings"
    __table_args__ = (UniqueConstraint("building_id", "timestamp", name="uq_energy_reading"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[str] = mapped_column(String(64), index=True, default="building-59")
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    total_kw: Mapped[float] = mapped_column(Float)
    interval_minutes: Mapped[float] = mapped_column(Float, default=15.0)
    source_file: Mapped[str] = mapped_column(String(128), default="ele.csv")
    quality_flag: Mapped[str | None] = mapped_column(String(64), nullable=True)


class OccupancyReading(Base):
    __tablename__ = "occupancy_readings"
    __table_args__ = (UniqueConstraint("building_id", "timestamp", name="uq_occupancy_reading"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[str] = mapped_column(String(64), index=True, default="building-59")
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    occupancy_count: Mapped[float] = mapped_column(Float)
    source_file: Mapped[str] = mapped_column(String(128), default="occ.csv")
    coverage_status: Mapped[str] = mapped_column(String(32), default="observed")


class WifiReading(Base):
    __tablename__ = "wifi_readings"
    __table_args__ = (UniqueConstraint("building_id", "timestamp", name="uq_wifi_reading"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[str] = mapped_column(String(64), index=True, default="building-59")
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    device_count: Mapped[float] = mapped_column(Float)
    source_file: Mapped[str] = mapped_column(String(128), default="wifi.csv")
    coverage_status: Mapped[str] = mapped_column(String(32), default="observed_proxy")


class WeatherReading(Base):
    __tablename__ = "weather_readings"
    __table_args__ = (UniqueConstraint("building_id", "timestamp", name="uq_weather_reading"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[str] = mapped_column(String(64), index=True, default="building-59")
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    air_temp_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    relative_humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    solar_radiation: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_file: Mapped[str] = mapped_column(String(128), default="site_weather.csv")


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    building_id: Mapped[str] = mapped_column(String(64), index=True, default="building-59")
    fingerprint: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(20), default="new", index=True)
    severity: Mapped[str] = mapped_column(String(20), index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    occupancy_value: Mapped[float] = mapped_column(Float, default=0.0)
    actual_kwh: Mapped[float] = mapped_column(Float)
    expected_kwh: Mapped[float] = mapped_column(Float)
    excess_kwh: Mapped[float] = mapped_column(Float)
    deviation_percent: Mapped[float] = mapped_column(Float)
    estimated_cost_usd: Mapped[float] = mapped_column(Float)
    estimated_co2_kg: Mapped[float] = mapped_column(Float)
    confidence: Mapped[str] = mapped_column(String(20))
    baseline_method: Mapped[str] = mapped_column(String(160))
    baseline_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    policy_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    schedule_context: Mapped[str | None] = mapped_column(String(120), nullable=True)
    data_quality_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    intervals: Mapped[list["AnomalyInterval"]] = relationship(back_populates="event", cascade="all, delete-orphan", order_by="AnomalyInterval.timestamp")


class AnomalyInterval(Base):
    __tablename__ = "anomaly_intervals"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("anomaly_events.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    interval_minutes: Mapped[float] = mapped_column(Float)
    actual_kwh: Mapped[float] = mapped_column(Float)
    expected_kwh: Mapped[float] = mapped_column(Float)
    occupancy_value: Mapped[float] = mapped_column(Float, default=0.0)
    occupancy_unit: Mapped[str] = mapped_column(String(32), default="people")
    occupancy_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    schedule_context: Mapped[str | None] = mapped_column(String(120), nullable=True)
    baseline_support: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data_quality: Mapped[str | None] = mapped_column(String(160), nullable=True)
    is_anomalous: Mapped[bool] = mapped_column(Boolean, default=True)
    event: Mapped[AnomalyEvent] = relationship(back_populates="intervals")
