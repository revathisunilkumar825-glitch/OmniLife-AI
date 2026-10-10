"""Tests for Member 4's database layer."""
import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from database import crud
from database.db import engine
from database.security import hash_password, verify_password


# ------------------------------------------------------------------ schema --
def test_all_tables_exist(db):
    tables = set(inspect(engine).get_table_names())
    assert {"users", "documents", "embeddings", "search_history"} <= tables


# ------------------------------------------------------------------- users --
def test_create_user_lowercases_email(db):
    u = crud.create_user(db, "Asha", "  Asha@Example.COM ", "hash")
    assert u.email == "asha@example.com"
    assert crud.get_user_by_email(db, "ASHA@example.com").id == u.id


def test_duplicate_email_is_rejected(db, user):
    with pytest.raises(IntegrityError):
        crud.create_user(db, "Other", "test@example.com", "hash")
    db.rollback()


def test_password_is_hashed_not_plain(user):
    assert user.password_hash != "Passw0rd!"
    assert verify_password("Passw0rd!", user.password_hash)
    assert not verify_password("wrong-password", user.password_hash)


def test_same_password_gives_different_hashes():
    # proves a random salt is used
    assert hash_password("same") != hash_password("same")


# --------------------------------------------------------------- documents --
def _doc(db, user, title="Resume", file_type="pdf", size=1000, category="resume"):
    return crud.add_document(db, user.id, title, f"{title}.pdf", f"uploads/pdf/{title}.pdf",
                             file_type, size, category)


def test_add_and_get_document(db, user):
    d = _doc(db, user)
    assert d.id and d.upload_date is not None
    assert crud.get_document(db, d.id, user.id).title == "Resume"


def test_user_cannot_read_or_delete_another_users_document(db, user):
    other = crud.create_user(db, "Mallory", "mallory@example.com", "hash")
    d = _doc(db, user)
    assert crud.get_document(db, d.id, other.id) is None
    assert crud.delete_document(db, d.id, other.id) is False
    assert crud.get_document(db, d.id, user.id) is not None
    assert crud.list_documents(db, other.id) == []


def test_update_document_ai_changes_only_given_fields(db, user):
    d = _doc(db, user)
    crud.update_document_ai(db, d.id, summary="First summary")
    crud.update_document_ai(db, d.id, tags=["python", " resume ", ""])
    d = crud.get_document(db, d.id, user.id)
    assert d.summary == "First summary"          # untouched by the 2nd call
    assert d.tags == "python,resume"
    assert d.tag_list == ["python", "resume"]


def test_update_unknown_document_returns_none(db):
    assert crud.update_document_ai(db, 9999, summary="x") is None


def test_list_documents_filters_and_orders_newest_first(db, user):
    a = _doc(db, user, "A", category="notes")
    b = _doc(db, user, "B", category="resume")
    c = _doc(db, user, "C", category="resume")
    assert [d.id for d in crud.list_documents(db, user.id)] == [c.id, b.id, a.id]
    assert {d.id for d in crud.list_documents(db, user.id, category="resume")} == {b.id, c.id}


def test_get_documents_by_ids_keeps_search_ranking(db, user):
    a, b, c = (_doc(db, user, t) for t in "ABC")
    got = crud.get_documents_by_ids(db, user.id, [c.id, a.id, b.id])
    assert [d.id for d in got] == [c.id, a.id, b.id]


def test_deleting_user_cascades_to_everything(db, user):
    d = _doc(db, user)
    crud.save_embedding(db, d.id, [0.1, 0.2])
    crud.log_search(db, user.id, "resume", 1)
    db.delete(user)
    db.commit()
    assert crud.load_embeddings(db) == []
    assert db.query(crud.Document).count() == 0
    assert db.query(crud.SearchHistory).count() == 0


# -------------------------------------------------------------- embeddings --
def test_embedding_roundtrip(db, user):
    d = _doc(db, user)
    vec = [0.5, -1.25, 3.0, 0.0]
    emb = crud.save_embedding(db, d.id, vec)
    assert emb.dim == 4
    (doc_id, loaded), = crud.load_embeddings(db, user.id)
    assert doc_id == d.id
    assert loaded == pytest.approx(vec)


def test_save_embedding_replaces_existing(db, user):
    d = _doc(db, user)
    crud.save_embedding(db, d.id, [1.0, 2.0])
    crud.save_embedding(db, d.id, [9.0, 8.0, 7.0])
    rows = crud.load_embeddings(db, user.id)
    assert len(rows) == 1 and rows[0][1] == pytest.approx([9.0, 8.0, 7.0])


def test_384_dimension_vector_like_minilm(db, user):
    d = _doc(db, user)
    vec = [i / 384 for i in range(384)]
    assert crud.save_embedding(db, d.id, vec).dim == 384
    assert crud.load_embeddings(db, user.id)[0][1] == pytest.approx(vec)


def test_load_embeddings_is_scoped_per_user(db, user):
    other = crud.create_user(db, "Bob", "bob@example.com", "hash")
    crud.save_embedding(db, _doc(db, user).id, [1.0])
    crud.save_embedding(db, _doc(db, other, "Z").id, [2.0])
    assert len(crud.load_embeddings(db, user.id)) == 1
    assert len(crud.load_embeddings(db)) == 2


# ----------------------------------------------------- history + dashboard --
def test_recent_searches_newest_first_and_limited(db, user):
    for q in ["one", "two", "three"]:
        crud.log_search(db, user.id, q, 2)
    got = crud.recent_searches(db, user.id, limit=2)
    assert [s.query for s in got] == ["three", "two"]


def test_dashboard_stats(db, user):
    p = _doc(db, user, "P", "pdf", 2000, "invoice")
    _doc(db, user, "I", "image", 500, "certificate")
    crud.update_document_ai(db, p.id, tags=["finance", "invoice"])
    crud.log_search(db, user.id, "laptop bill", 1)

    s = crud.dashboard_stats(db, user.id)
    assert s["total_files"] == 2
    assert (s["pdfs"], s["images"]) == (1, 1)
    assert s["storage_used_bytes"] == 2500
    assert s["categories"] == {"invoice": 1, "certificate": 1}
    assert s["ai_tags_total"] == 2
    assert s["recent_searches"][0]["query"] == "laptop bill"
    assert len(s["recent_uploads"]) == 2


def test_dashboard_for_new_user_is_all_zero(db, user):
    s = crud.dashboard_stats(db, user.id)
    assert s["total_files"] == 0 and s["storage_used_bytes"] == 0
    assert s["categories"] == {} and s["recent_uploads"] == []
