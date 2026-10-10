# Member 4 guide - Database + DevOps (step by step, for beginners)

You do not need to know anything about the project in advance. Follow the
parts in order; each one tells you what to type and what you should see.

**Your responsibilities (from the PDF):** Database · Testing · GitHub · Deployment

| Responsibility | Where it lives | Part of this guide |
|---|---|---|
| Database | `database/` | Parts 3-5 |
| Testing | `tests/`, `documents/test_dataset/` | Part 6 |
| GitHub | `.github/`, `docs/GIT_WORKFLOW.md` | Part 7 |
| Deployment | `Dockerfile`, `docker-compose.yml` | Part 8 |

---

## Part 1 - Install the tools (once)

1. **Python 3.12** from python.org (tick *Add Python to PATH* on Windows). Check: `python --version`
2. **Git** from git-scm.com. Check: `git --version`
3. **VS Code** from code.visualstudio.com, then open the **Extensions** panel (`Ctrl+Shift+X`) and install: *Python*, *Pylance*, *GitLens*, *SQLite Viewer*. (When you open this project VS Code will also suggest the others from `.vscode/extensions.json` - click *Install All*.)
4. *(Optional, Part 8)* **Docker Desktop** from docker.com.

## Part 2 - Open the project and create a virtual environment

A virtual environment is a private box of Python packages for this project only.

In VS Code: **File → Open Folder → `OmniLife-AI`**, then open the terminal with `Ctrl + ~`.

```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

You should now see `(.venv)` at the start of the prompt. (If PowerShell blocks the
script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.)
VS Code may ask *"Use this environment?"* - click **Yes**.

Install what Member 4 needs (small and fast):

```bash
pip install -r requirements-ci.txt
```

> `requirements.txt` is the **full** list for the whole team (it downloads PyTorch,
> several GB). You only need `requirements-ci.txt` for database work and tests.

## Part 3 - Run the database for the first time

Always run commands from the project root (the folder that contains `database/`).

```bash
python -m database.init_db
```
You should see: `Tables: documents, embeddings, search_history, users` - and a new file `database/app.db` exists. That file **is** the database (SQLite).

```bash
python -m database.generate_test_dataset    # creates 25 fake PDFs + manifest.json
python -m database.seed                     # puts them into the database
```
You should see `Seed complete: 25 new documents`.

**Look inside the database:** in VS Code click `database/app.db` (the *SQLite Viewer*
extension opens it) and browse the `users`, `documents`, `embeddings` and
`search_history` tables. The demo login is `demo@omnilife.test` / `Demo@12345`.

## Part 4 - What each file does (so you can explain it)

| File | In plain words |
|---|---|
| `database/schema.sql` | The tables written in SQL. Use it to draw the ER diagram for your project report. |
| `database/db.py` | Opens the connection to the database. SQLite by default; set `DATABASE_URL` to use PostgreSQL. Also gives `get_db()` for the API. |
| `database/models.py` | Python classes = tables: `User`, `Document`, `Embedding`, `SearchHistory`. (SQLAlchemy turns these into tables.) |
| `database/crud.py` | Ready-made functions the team calls (create user, add document, dashboard numbers…). Create/Read/Update/Delete = **CRUD**. |
| `database/security.py` | Hashes passwords. We **never** store the real password. |
| `database/init_db.py` | Creates the tables. |
| `database/generate_test_dataset.py` | Makes the 25 fake test PDFs. |
| `database/seed.py` | Loads the fake PDFs into the DB so everyone can test with data. |

**The tables (matches the PDF's design, plus one extra):**

```
users            documents                         embeddings          search_history
────────         ───────────────────────────       ────────────        ──────────────
id (PK)    ◄──┐  id (PK)                          id (PK)             id (PK)
name          └─ user_id (FK)            ◄───────  document_id (FK)    user_id (FK) ──► users
email (unique)   title, filename, filepath         dim                 query
password_hash    file_type, file_size, category    vector (bytes)      result_count
created_at       extracted_text, summary, tags                         searched_at
                 upload_date
```

Small changes vs the PDF, and why (good viva answers):
- `password` → **`password_hash`**: storing a plain password would be a security flaw.
- `documents` has extra columns `file_type`, `file_size` (dashboard: PDFs/images, storage used), `category` (dashboard categories) and `extracted_text` (the OCR/PDF text, needed to re-create summaries and embeddings).
- `search_history` is new: the dashboard shows "Recent Searches".
- `embeddings.vector` is stored as bytes (`float32`), with `dim` (384 for the MiniLM model). FAISS is the fast search index built *from* these rows.

## Part 5 - Call the database from Python (try it!)

Create a scratch file `try_db.py` in the project root:

```python
from database.db import SessionLocal
from database import crud

db = SessionLocal()
user = crud.get_user_by_email(db, "demo@omnilife.test")

for doc in crud.list_documents(db, user.id, category="resume"):
    print(doc.title, "|", doc.tag_list)

print(crud.dashboard_stats(db, user.id)["categories"])
db.close()
```
Run it: `python try_db.py`. You just used the same functions the API will use.
(Delete the file afterwards - or don't commit it.)

**Switching to PostgreSQL later** (optional, only if your guide asks for it):
1. `docker compose --profile postgres up -d postgres`
2. `pip install psycopg2-binary`
3. In `.env` set `DATABASE_URL=postgresql+psycopg2://omnilife:<your POSTGRES_PASSWORD>@localhost:5432/omnilife`
4. `python -m database.init_db`

No Python code changes. (The code was tested on SQLite; the PostgreSQL path
uses standard SQLAlchemy but was not run against a live PostgreSQL server.)

## Part 6 - Testing

```bash
python -m pytest
```
Expected: **`28 passed, 1 skipped`**. The skipped one is the semantic-search test; it
switches on by itself when Member 3 creates `ai/search.py`.

What is tested:
- **Database:** users, unique emails, password hashing, documents, cascade delete, embeddings round-trip, dashboard numbers.
- **Security:** user B cannot read or delete user A's documents (prevents IDOR).
- **FastAPI integration:** the DB works inside API routes.
- **Dataset:** 25 PDFs, 5 per category, all readable, ID documents are marked MOCK.
- **Search quality:** 18 queries with known correct answers (Step 15 of the PDF).

In VS Code you can also click the **flask icon (Testing)** in the left bar and run tests with a button.

**See why semantic search matters:**
```bash
python -m tests.search_eval
```
A plain keyword search gets 12/12 on keyword-style queries but only **1/6** on
reworded ones like *"what do I owe the power company"* (answer: the electricity bill).
Member 3's search must do better - that is your evidence slide.

> The test data is fake on purpose. Never put real Aadhaar/PAN/passport files in GitHub or a demo.

## Part 7 - GitHub

Follow `docs/GIT_WORKFLOW.md` (create the repo, branches, branch protection, daily routine).
The CI robot in `.github/workflows/ci.yml` then runs `pytest` on every push and pull request -
you will see a green tick or red cross on GitHub.

## Part 8 - Deployment with Docker (optional in the PDF)

Docker packages the app so it runs identically on any computer.

```bash
cp .env.example .env          # Windows: copy .env.example .env   - then edit the values
docker compose up --build     # backend on :8000, frontend on :3000
```
It only works after Member 2 creates `backend/main.py` (with `GET /health`) and
Member 1 creates the Vite app in `frontend/`.

> **Honest status:** the compose file passes `docker compose config` validation, but the
> images could not be built in the environment where this was prepared (no Docker
> engine available there), so do a first build early and fix any package problem
> while there is still time. The first build downloads several GB (PyTorch).

Security choices in the Dockerfile worth mentioning: runs as a non-root user, secrets come from `.env` (never baked into the image), `.dockerignore` keeps `.env` and uploads out of the image.

## Part 9 - Your 14-day plan (from the PDF's timeline)

| Days | Your job |
|---|---|
| 1-2 | Create repo + branches, finish DB design, share `docs/TEAM_CONTRACT.md` |
| 3-4 | Help Member 2 connect `get_db`/`crud`; run `seed` for everyone |
| 5-8 | Keep CI green; review pull requests; check Dockerfile builds |
| 9-10 | Run `tests/test_search_quality.py` against Member 3's search; report failing queries |
| 11-12 | Integration testing, bug triage |
| 13 | Full test run, final README, clean `git status` |
| 14 | Final demo (use the Part 6 test results as evidence) |

More viva practice: `docs/VIVA_PREP.md`.
