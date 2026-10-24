"""Dashboard, schedule-aware anomaly investigation, and Building 59 ingestion endpoints."""

from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.ml.baseline_detector import ScheduleAwareBaselineModel
from app.schemas.anomaly import AnomalyEventDetail, AnomalyListResponse, ClearDataResponse, DetectionResponse, IngestionRequest, IngestionResponse, UpdateEventStatusRequest
from app.schemas.dashboard import DashboardResponse
from app.services.anomaly_service import dashboard, event_detail, get_event_detail, list_event_summaries, list_events, run_detection
from app.services.ingestion_service import BUILDING_ID, clear_building_59, ingest_building_59

router = APIRouter(tags=["anomalies"])
VALID_STATUSES = {"new", "investigating", "resolved", "dismissed"}

@router.post("/ingestion/building-59", response_model=IngestionResponse, status_code=status.HTTP_201_CREATED)
def ingest_building_data(payload: IngestionRequest, db: Session = Depends(get_db)) -> IngestionResponse:
    source_dir = Path(payload.source_dir) if payload.source_dir else settings.BUILDING_59_DATA_DIR
    try:
        result = ingest_building_59(db, source_dir)
        event_count = run_detection(db, BUILDING_ID)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
    return IngestionResponse(building_id=BUILDING_ID, energy_readings=result.energy_readings, occupancy_intervals=result.occupancy_intervals, wifi_intervals=result.wifi_intervals, weather_intervals=result.weather_intervals, anomaly_events=event_count, source_dir=str(source_dir.expanduser().resolve()))

@router.delete("/ingestion/building-59", response_model=ClearDataResponse)
def clear_building_data(db: Session = Depends(get_db)) -> ClearDataResponse:
    """Permanently clear imported Building 59 data and generated anomaly events."""
    result = clear_building_59(db)
    return ClearDataResponse(
        building_id=BUILDING_ID,
        energy_readings_deleted=result.energy_readings,
        occupancy_intervals_deleted=result.occupancy_intervals,
        wifi_intervals_deleted=result.wifi_intervals,
        weather_intervals_deleted=result.weather_intervals,
        anomaly_events_deleted=result.anomaly_events,
        message="Building 59 data and anomaly events were cleared. Import a data folder to analyze again.",
    )

@router.post("/detection/building-59", response_model=DetectionResponse)
def refresh_detection(db: Session = Depends(get_db)) -> DetectionResponse:
    event_count = run_detection(db, BUILDING_ID)
    if event_count == 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No schedule-qualified anomaly candidates are available. Ingest Building 59 first or adjust policy thresholds.")
    return DetectionResponse(building_id=BUILDING_ID, anomaly_events=event_count, policy_version=settings.DETECTION_POLICY.version, baseline_version=ScheduleAwareBaselineModel.version, message="Historical schedule-aware baseline analysis completed.")

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(building_id: str = BUILDING_ID, start: datetime | None = None, end: datetime | None = None, db: Session = Depends(get_db)) -> DashboardResponse:
    if start and end and start > end:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="start must be before end")
    return DashboardResponse.model_validate(dashboard(db, building_id, start, end))

@router.get("/anomalies", response_model=AnomalyListResponse)
def get_anomalies(building_id: str = BUILDING_ID, status_filter: str | None = Query(default=None, alias="status"), limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)) -> AnomalyListResponse:
    if status_filter and status_filter not in VALID_STATUSES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid anomaly status")
    items = list_event_summaries(db, building_id, status_filter, limit)
    return AnomalyListResponse(items=items, total=len(list_events(db, building_id, status_filter, 100_000)))

@router.get("/anomalies/{event_id}", response_model=AnomalyEventDetail)
def get_anomaly(event_id: str, db: Session = Depends(get_db)) -> AnomalyEventDetail:
    event = get_event_detail(db, event_id)
    if event is None: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anomaly event not found")
    return AnomalyEventDetail.model_validate(event_detail(event))

@router.patch("/anomalies/{event_id}/status", response_model=AnomalyEventDetail)
def update_anomaly_status(event_id: str, payload: UpdateEventStatusRequest, db: Session = Depends(get_db)) -> AnomalyEventDetail:
    event = get_event_detail(db, event_id)
    if event is None: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anomaly event not found")
    event.status = payload.status; db.commit(); db.refresh(event)
    return AnomalyEventDetail.model_validate(event_detail(event))
