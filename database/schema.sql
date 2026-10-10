-- OmniLife AI - database schema (SQLite flavour; works on PostgreSQL with
-- INTEGER PRIMARY KEY AUTOINCREMENT -> SERIAL PRIMARY KEY and BLOB -> BYTEA).
-- The SQLAlchemy models in database/models.py create the same tables, so you
-- normally run `python -m database.init_db`. This file is the documented
-- reference (and is handy for the ER diagram in the presentation).

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL,
    email          TEXT    NOT NULL UNIQUE,
    password_hash  TEXT    NOT NULL,            -- never store plain passwords
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title        TEXT    NOT NULL,
    filename     TEXT    NOT NULL,              -- original name shown to the user
    filepath     TEXT    NOT NULL,              -- where the file is stored on disk
    file_type    TEXT    NOT NULL,              -- 'pdf' or 'image'
    file_size    INTEGER NOT NULL DEFAULT 0,    -- bytes (dashboard: storage used)
    category     TEXT,                          -- certificate, invoice, resume, ...
    extracted_text TEXT,                        -- output of PyMuPDF / EasyOCR
    summary      TEXT,                          -- AI summary
    tags         TEXT,                          -- comma separated AI tags
    upload_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);

CREATE TABLE IF NOT EXISTS embeddings (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id  INTEGER NOT NULL UNIQUE REFERENCES documents(id) ON DELETE CASCADE,
    dim          INTEGER NOT NULL,              -- vector length (384 for MiniLM)
    vector       BLOB    NOT NULL               -- float32 values packed as bytes
);

-- Needed for the dashboard card "Recent Searches".
CREATE TABLE IF NOT EXISTS search_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query        TEXT    NOT NULL,
    result_count INTEGER NOT NULL DEFAULT 0,
    searched_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_search_user ON search_history(user_id);
