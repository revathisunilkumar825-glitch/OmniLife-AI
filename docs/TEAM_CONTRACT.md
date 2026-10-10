# Team contract: how the 4 parts plug together

Member 4 (database) owns the `database/` package. The others **import it** -
nobody writes their own SQL or their own table definitions. Agree on this
document on Day 1 and most integration bugs disappear.

**Golden rule:** run every Python command from the **project root**
(the folder containing `database/`, `backend/`, `ai/`):

```bash
uvicorn backend.main:app --reload       # NOT: cd backend && uvicorn main:app
python -m database.init_db
python -m pytest
```

## What Member 4 provides

| Need | Import | Notes |
|------|--------|-------|
| DB session in an API route | `from database.db import get_db` | use as `db = Depends(get_db)` |
| Table classes | `from database.models import User, Document, Embedding, SearchHistory` | |
| Ready-made queries | `from database import crud` | table below |
| Password hashing | `from database.security import hash_password, verify_password` | PBKDF2-SHA256 via passlib |
| Switch to PostgreSQL | set `DATABASE_URL` in `.env` | no code change |
| Mock data for testing | `python -m database.seed` | login `demo@omnilife.test` / `Demo@12345` |

### `crud` functions

| Function | Used by | Purpose |
|----------|---------|---------|
| `create_user(db, name, email, password_hash)` | Member 2 `/register` | email is lower-cased; duplicate email raises `IntegrityError` - check `get_user_by_email` first |
| `get_user_by_email(db, email)` / `get_user(db, id)` | Member 2 `/login`, JWT dependency | |
| `add_document(db, user_id, title, filename, filepath, file_type, file_size, category)` | Member 2 `/upload` | `file_type` is `"pdf"` or `"image"` |
| `update_document_ai(db, doc_id, extracted_text=, summary=, tags=, category=)` | Member 3 pipeline | only the fields you pass are changed; `tags` is a list of strings |
| `save_embedding(db, doc_id, vector)` | Member 3 | list or numpy array; replaces an existing one |
| `load_embeddings(db, user_id=None)` | Member 3 | `[(doc_id, [floats]), ...]` to rebuild the FAISS index |
| `get_documents_by_ids(db, user_id, ids)` | Member 2 `/search` | returns documents in the same order as `ids` (best match first) |
| `list_documents(db, user_id, category=None, limit=50, offset=0)` | Member 2 `/documents` | newest first |
| `get_document(db, doc_id, user_id)` / `delete_document(...)` | Member 2 | |
| `log_search(db, user_id, query, result_count)` | Member 2 `/search` | feeds "Recent Searches" |
| `dashboard_stats(db, user_id)` | Member 2 `/dashboard` → Member 1 | one call returns everything the dashboard shows |

**Every document function takes `user_id`.** Always pass the id of the
*logged-in user* (taken from the JWT, never from the URL or request body) so
one user can never read another user's files.

### Shape of `dashboard_stats` (Member 1 builds the cards from this)

```json
{
  "total_files": 25, "pdfs": 25, "images": 0,
  "storage_used_bytes": 29174,
  "categories": {"certificate": 5, "notes": 5, "identity": 5, "invoice": 5, "resume": 5},
  "ai_tags_total": 115,
  "top_tags": [["certificate", 5], ["notes", 5], ["identity", 5]],
  "recent_uploads":  [{"id": 3, "title": "...", "upload_date": "2026-10-10T10:00:00"}],
  "recent_searches": [{"query": "Find Aadhaar", "result_count": 1, "searched_at": "..."}]
}
```

## What Member 4 needs from the others

**Member 2 (backend)**
- `backend/main.py` exposing `app` (FastAPI) and `GET /health` returning 200 - Docker and the demo use it.
- Endpoints from the PDF: `POST /register`, `POST /login`, `POST /upload`, `GET /search`, `GET /documents`, plus `GET /dashboard` (calls `crud.dashboard_stats`).
- JWT secret read from the `SECRET_KEY` environment variable, never hard-coded.
- Upload flow: validate type/size → save with a random server-side filename → `add_document` → AI pipeline → `update_document_ai` + `save_embedding`.

**Member 3 (AI)**
- `ai/search.py` with `search(query: str, user_id: int, top_k: int = 5) -> list[int]` returning `Document.id` values, best first. `tests/test_search_quality.py` switches on automatically when this file exists.
- Optional `build_index()` in the same file - the test calls it after seeding.
- Vectors stored via `crud.save_embedding`; the FAISS index is *derived data* that can always be rebuilt from the `embeddings` table. (all-MiniLM-L6-v2 gives 384 numbers per vector.)
- Target: ≥ 15 of 18 test queries find the right file in the top 3 (`python -m tests.search_eval` shows how a plain keyword search scores - your job is to beat it, especially on the paraphrase queries).

**Member 1 (frontend)**
- Put the Vite project directly in `frontend/` (so `frontend/package.json` exists) - CI and `frontend/Dockerfile` pick it up automatically.
- Backend URL comes from `VITE_API_URL`.
