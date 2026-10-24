"""App-wide settings. Override values with environment variables."""

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings:
    APP_NAME: str = "GhostWatt API"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'ghostwatt.db'}"
    )
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")


settings = Settings()
