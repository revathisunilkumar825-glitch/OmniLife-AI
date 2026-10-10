"""Proves the database layer plugs into FastAPI the way Member 2 will use it
(Depends(get_db) + crud functions), including across FastAPI's worker threads.
This builds a tiny throw-away app; the real one lives in backend/main.py."""
import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

from database import crud
from database.db import get_db
from database.security import hash_password

app = FastAPI()


@app.post("/register")
def register(payload: dict, db=Depends(get_db)):
    if crud.get_user_by_email(db, payload["email"]):
        raise HTTPException(409, "Email already registered")
    user = crud.create_user(db, payload["name"], payload["email"],
                            hash_password(payload["password"]))
    return {"id": user.id}


@app.get("/documents")
def documents(user_id: int, db=Depends(get_db)):
    return [{"id": d.id, "title": d.title} for d in crud.list_documents(db, user_id)]


@app.get("/dashboard")
def dashboard(user_id: int, db=Depends(get_db)):
    return crud.dashboard_stats(db, user_id)


@pytest.fixture()
def client(db):          # `db` fixture gives a clean database for each test
    return TestClient(app)


def test_register_then_duplicate_is_409(client):
    body = {"name": "Asha", "email": "asha@example.com", "password": "Secret#123"}
    first = client.post("/register", json=body)
    assert first.status_code == 200
    assert client.post("/register", json=body).status_code == 409


def test_documents_and_dashboard_through_the_api(client, db):
    uid = client.post("/register", json={"name": "A", "email": "a@x.com",
                                         "password": "pw"}).json()["id"]
    crud.add_document(db, uid, "My Resume", "r.pdf", "uploads/pdf/r.pdf", "pdf", 1234, "resume")
    assert client.get("/documents", params={"user_id": uid}).json()[0]["title"] == "My Resume"
    stats = client.get("/dashboard", params={"user_id": uid}).json()
    assert stats["total_files"] == 1 and stats["storage_used_bytes"] == 1234
