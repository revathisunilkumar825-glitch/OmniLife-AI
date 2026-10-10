"""Database connection setup.

Default: SQLite file at database/app.db  (zero setup, perfect for the MVP).
To switch to PostgreSQL, set an environment variable, no code change needed:

    DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/omnilife
"""
import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SQLITE_URL = f"sqlite:///{BASE_DIR / 'app.db'}"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

_is_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    # SQLite objects are shared across FastAPI worker threads
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    future=True,
)

if _is_sqlite:
    # SQLite ignores foreign keys unless you switch them on per connection.
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    """FastAPI dependency (Member 2 uses this):

        from fastapi import Depends
        from database.db import get_db

        @app.get("/documents")
        def list_docs(db = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
