from fastapi import APIRouter

from app.schemas.hello import HelloResponse

router = APIRouter()


@router.get("/hello", response_model=HelloResponse)
def hello() -> HelloResponse:
    return HelloResponse(message="Hello World from GhostWatts")
