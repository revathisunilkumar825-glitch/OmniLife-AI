"""Search-quality test for Member 3's semantic search.

It SKIPS automatically until ai/search.py exists, then starts running.

Contract Member 3 agrees to (see docs/TEAM_CONTRACT.md):

    ai/search.py
        def search(query: str, user_id: int, top_k: int = 5) -> list[int]:
            '''Return document ids (Document.id), best match first.'''

    Optional: if ai/search.py also defines build_index(), this test calls it
    once, after the mock data has been seeded, so the index can be built from
    the database (summaries/embeddings of the seeded documents).
"""
import pytest

from database import crud, seed
from database.db import SessionLocal
from tests.search_eval import evaluate

search_module = pytest.importorskip(
    "ai.search", reason="ai/search.py not written yet (Member 3)")

MIN_ACCURACY = 0.80   # agreed target: 15 of 18 queries find the right file in top 3


def test_semantic_search_finds_the_right_documents():
    seed.seed(reset=True)
    if hasattr(search_module, "build_index"):
        search_module.build_index()

    db = SessionLocal()
    try:
        user = crud.get_user_by_email(db, seed.DEMO_EMAIL)
        id_to_slug = {d.id: d.filename.removesuffix(".pdf")
                      for d in crud.list_documents(db, user.id, limit=1000)}

        def search_fn(query):
            ids = search_module.search(query, user.id, top_k=3)
            return [id_to_slug[i] for i in ids if i in id_to_slug]

        report = evaluate(search_fn, top_k=3)
    finally:
        db.close()

    failed = [r for r in report["details"] if not r["hit"]]
    assert report["accuracy"] >= MIN_ACCURACY, (
        f"{report['hits']}/{report['total']} correct. Failed: {failed}")
