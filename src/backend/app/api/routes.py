"""Top-level API router registration."""

from fastapi import APIRouter

from app.api.anomalies import router as anomalies_router
from app.schemas.hello import HelloResponse

router = APIRouter()
router.include_router(anomalies_router)


@router.get("/hello", response_model=HelloResponse)
def hello() -> HelloResponse:
    return HelloResponse(message="Hello from GhostWatt")
