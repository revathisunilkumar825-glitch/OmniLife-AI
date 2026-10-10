# OmniLife AI - Personal Memory Search Engine

> *Search your life like Google.* Upload PDFs and images; AI extracts the text,
> summarises it, tags it, and lets you find any file with a natural-language query.

MCA final year project - team of 4.

| Member | Role | Folder |
|---|---|---|
| 1 | Frontend (React + Tailwind) | `frontend/` |
| 2 | Backend (FastAPI, JWT, uploads) | `backend/` |
| 3 | AI (OCR, summaries, embeddings, FAISS) | `ai/` |
| 4 | Database + DevOps (tests, GitHub, Docker) | `database/`, `tests/`, `.github/`, `docs/` |

## Quick start (database + tests)

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-ci.txt

python -m database.init_db                  # create tables
python -m database.generate_test_dataset    # 25 fake PDFs
python -m database.seed                     # load them (demo@omnilife.test / Demo@12345)
python -m pytest                            # 28 passed, 1 skipped
```

Run everything from the project root. Full installation (AI libraries): `pip install -r requirements.txt`.

## Workflow

```
Upload → store file → extract text (PDF / OCR) → AI summary → AI tags
       → embeddings → save in database → natural-language search → results
```

## Documentation

- `docs/MEMBER4_GUIDE.md` - step-by-step walkthrough (database, tests, GitHub, Docker)
- `docs/TEAM_CONTRACT.md` - how the four parts connect (functions, endpoints, JSON shapes)
- `docs/GIT_WORKFLOW.md` - branches, pull requests, conflicts, security habits
- `docs/VIVA_PREP.md` - likely viva questions with answers

## Project layout

```
OmniLife-AI/
├── frontend/      React app (Member 1)
├── backend/       FastAPI app (Member 2)      api/ auth/ models/ services/ uploads/ main.py
├── ai/            ocr.py summarizer.py embeddings.py search.py (Member 3)
├── database/      schema.sql, models, crud, seed, init_db   (Member 4)
├── tests/         pytest suite + search evaluation          (Member 4)
├── documents/     mock test dataset (fake data only)
├── uploads/       user files at runtime (git-ignored)
├── Dockerfile, docker-compose.yml, .github/workflows/ci.yml
└── README.md
```

## Privacy note

Only fictional, clearly marked mock documents are in this repository. Never
commit real identity documents, `.env` files or the live `database/app.db`.
