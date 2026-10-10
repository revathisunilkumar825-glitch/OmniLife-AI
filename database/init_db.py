"""Create all tables.   Run from the project root:

    python -m database.init_db
"""
from . import models  # noqa: F401  (registers the tables on Base)
from .db import DATABASE_URL, Base, engine


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    tables = ", ".join(sorted(Base.metadata.tables))
    print(f"Database ready at {DATABASE_URL}")
    print(f"Tables: {tables}")
