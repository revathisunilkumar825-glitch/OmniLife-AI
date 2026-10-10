"""Test setup: every test run uses its own throw-away SQLite file so the real
database/app.db is never touched. DATABASE_URL must be set BEFORE importing
anything from the `database` package (the engine is created at import time)."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp_dir = tempfile.mkdtemp(prefix="omnilife_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_tmp_dir) / 'test.db'}"

import pytest  # noqa: E402

from database import models  # noqa: E402,F401
from database.db import Base, SessionLocal, engine  # noqa: E402


@pytest.fixture()
def db():
    """A clean database for every single test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def user(db):
    from database import crud
    from database.security import hash_password
    return crud.create_user(db, "Test User", "test@example.com", hash_password("Passw0rd!"))


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
