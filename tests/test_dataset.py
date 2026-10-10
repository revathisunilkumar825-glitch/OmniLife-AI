"""Tests for the mock dataset and the seed script."""
from collections import Counter

import pymupdf
import pytest

from database import crud, seed
from database.db import SessionLocal
from tests.search_eval import DATASET_DIR, evaluate, keyword_search, load_manifest


def test_dataset_has_25_documents_5_per_category():
    docs = load_manifest()["documents"]
    assert len(docs) == 25
    assert Counter(d["category"] for d in docs) == {
        "certificate": 5, "notes": 5, "identity": 5, "invoice": 5, "resume": 5}


def test_every_pdf_exists_and_has_readable_text():
    for d in load_manifest()["documents"]:
        path = DATASET_DIR / d["filename"]
        assert path.exists(), path
        with pymupdf.open(path) as pdf:
            text = "".join(page.get_text() for page in pdf)
        assert len(text.strip()) > 80, f"{d['filename']} has no extractable text"


def test_identity_documents_are_clearly_marked_mock():
    for d in load_manifest()["documents"]:
        if d["category"] == "identity":
            with pymupdf.open(DATASET_DIR / d["filename"]) as pdf:
                assert "NOT A REAL DOCUMENT" in pdf[0].get_text()


def test_every_expected_search_result_exists_in_manifest():
    manifest = load_manifest()
    slugs = {d["slug"] for d in manifest["documents"]}
    for q in manifest["queries"]:
        assert q["expected"] and set(q["expected"]) <= slugs


def test_seed_loads_everything_and_is_repeatable():
    seed.seed(reset=True)
    seed.seed()                     # 2nd run must not create duplicates
    db = SessionLocal()
    try:
        user = crud.get_user_by_email(db, seed.DEMO_EMAIL)
        stats = crud.dashboard_stats(db, user.id)
        assert stats["total_files"] == 25
        assert stats["categories"]["resume"] == 5
        assert stats["recent_searches"]
        doc = crud.list_documents(db, user.id, category="invoice")[0]
        assert doc.extracted_text and doc.summary and doc.tag_list
    finally:
        db.close()


def test_keyword_baseline_clears_the_bar_on_keyword_queries():
    """Sanity check of the evaluation harness itself."""
    report = evaluate(keyword_search, top_k=3, kind="keyword")
    assert report["accuracy"] >= 0.75, report["details"]


def test_paraphrase_queries_are_hard_for_keyword_search():
    """Documents WHY the project needs semantic search: plain keyword matching
    misses queries that mean the same thing in different words."""
    report = evaluate(keyword_search, top_k=3, kind="paraphrase")
    assert report["total"] >= 5
    assert report["accuracy"] <= 0.5, "dataset too easy - add harder paraphrases"
