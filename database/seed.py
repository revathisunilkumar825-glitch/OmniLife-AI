"""Load the mock dataset into the database so everybody can test with data
on day 1 (dashboard cards, document list, search) without uploading by hand.

    python -m database.generate_test_dataset     # once, creates the PDFs
    python -m database.seed                      # loads them
    python -m database.seed --reset              # wipe tables first

Demo login created:  demo@omnilife.test  /  Demo@12345   (change in real use!)

Embeddings are NOT created here - that is Member 3's pipeline. After seeding,
run their embedding step over documents that have no embedding yet.
"""
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pymupdf  # PyMuPDF

from . import crud
from .db import Base, SessionLocal, engine
from .init_db import init_db
from .security import hash_password

ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "documents" / "test_dataset"

DEMO_NAME = "Demo User"
DEMO_EMAIL = "demo@omnilife.test"
DEMO_PASSWORD = "Demo@12345"


def extract_pdf_text(path: Path) -> str:
    with pymupdf.open(path) as pdf:
        return "\n".join(page.get_text() for page in pdf).strip()


def seed(reset: bool = False) -> None:
    manifest_path = DATASET_DIR / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(
            "manifest.json not found. Run first:  python -m database.generate_test_dataset"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if reset:
        Base.metadata.drop_all(bind=engine)
    init_db()

    db = SessionLocal()
    try:
        user = crud.get_user_by_email(db, DEMO_EMAIL)
        if user is None:
            user = crud.create_user(db, DEMO_NAME, DEMO_EMAIL, hash_password(DEMO_PASSWORD))

        existing = {d.filename for d in crud.list_documents(db, user.id, limit=10_000)}
        added = 0
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        for i, item in enumerate(manifest["documents"]):
            if item["filename"] in existing:
                continue
            pdf_path = DATASET_DIR / item["filename"]
            doc = crud.add_document(
                db, user.id, title=item["title"], filename=item["filename"],
                filepath=str(pdf_path.relative_to(ROOT)), file_type="pdf",
                file_size=pdf_path.stat().st_size, category=item["category"],
            )
            crud.update_document_ai(
                db, doc.id, extracted_text=extract_pdf_text(pdf_path),
                summary=item["summary"], tags=item["tags"],
            )
            # spread upload dates so "Recent Uploads" looks realistic
            doc.upload_date = now - timedelta(hours=i)
            db.commit()
            added += 1

        for query, hits in [("Show my internship certificate", 1), ("Find Aadhaar", 1)]:
            crud.log_search(db, user.id, query, hits)

        print(f"Seed complete: {added} new documents (user: {DEMO_EMAIL})")
    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--reset", action="store_true", help="drop all tables first")
    seed(parser.parse_args().reset)
