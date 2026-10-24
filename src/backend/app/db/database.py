"""SQLAlchemy engine, development schema migration, and session setup."""

from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base class for app ORM models."""


# SQLite's create_all does not add columns to an existing hackathon database.
# Keep the small additive migration list explicit until a migration tool is adopted.
_ADDITIVE_COLUMNS = {
    "energy_readings": {"quality_flag": "VARCHAR(64)"},
    "occupancy_readings": {"coverage_status": "VARCHAR(32) DEFAULT 'observed'"},
    "anomaly_events": {
        "baseline_version": "VARCHAR(80)", "policy_version": "VARCHAR(80)",
        "schedule_context": "VARCHAR(120)", "data_quality_summary": "TEXT",
    },
    "anomaly_intervals": {
        "occupancy_source": "VARCHAR(32)", "schedule_context": "VARCHAR(120)",
        "baseline_support": "INTEGER", "data_quality": "VARCHAR(160)",
    },
}


def _apply_additive_migrations() -> None:
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table, additions in _ADDITIVE_COLUMNS.items():
            if table not in inspector.get_table_names():
                continue
            existing = {column["name"] for column in inspector.get_columns(table)}
            for column, definition in additions.items():
                if column not in existing:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))


def init_db() -> None:
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _apply_additive_migrations()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
