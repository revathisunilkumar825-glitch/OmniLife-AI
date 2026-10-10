# Viva preparation

The PDF lists likely viva questions. Short, honest answers you can build on.

**Why FastAPI instead of Flask?**
FastAPI validates request data automatically (Pydantic), generates interactive API docs at `/docs`, supports async code, and is fast. Flask needs extra libraries for the same things. It is also the usual choice for AI projects in Python.

**What is semantic search?**
Search by *meaning* instead of exact words. "What do I owe the power company" finds the electricity bill even though none of those words are in the file name. In this project keyword matching solved 12/12 literal queries but only 1/6 reworded ones (`python -m tests.search_eval`).

**What are embeddings?**
A list of numbers (384 for MiniLM) that represents the meaning of a text. Texts with similar meaning get vectors that are close together, so "nearest vector" = "most similar document".

**Why FAISS?**
A library from Meta that finds the nearest vectors very fast. We store each vector in the `embeddings` table (the permanent copy) and load them into a FAISS index for quick searching. The index can always be rebuilt from the table.

**How is AI generating summaries?**
The extracted text is sent to a local LLM (Llama 3 via Ollama) with a prompt like "summarise this document in one or two sentences". The result is stored in `documents.summary`. Running locally means documents never leave the user's computer.

**How does OCR work?**
EasyOCR (a neural network) finds text regions in an image and recognises the characters in each region. PDFs that already contain text are read directly with PyMuPDF; OCR is for images and scanned pages.

**How do you secure uploaded files?** *(your strong topic)*
- Allow-list file types (PDF/JPG/PNG), check the real content type (magic bytes), not just the extension, and set a size limit.
- Save under a random server-side name (UUID), never the user's file name (stops path traversal like `../../`).
- Store outside the web-served folder; never execute uploaded files.
- Authentication (JWT) + every query filtered by the logged-in `user_id` (tested in `tests/test_database.py`) so users cannot read each other's files.
- Passwords stored as salted PBKDF2 hashes; secrets in environment variables; HTTPS in production.
- Mock data only in GitHub; `.gitignore` blocks `.env`, uploads and the live database.

**How would you scale this to millions of documents?**
Move from SQLite to PostgreSQL (with the `pgvector` extension) or a vector database (Qdrant/Milvus); use an approximate FAISS index (IVF/HNSW) instead of exact search; store files in object storage (S3-style); process OCR and AI jobs in background workers with a queue (Celery/Redis) instead of during the upload request; run several API instances behind a load balancer; cache frequent searches.

## Questions specific to Member 4

**Why SQLite for the MVP, and when would you switch?**
It needs no server, one file, ideal for a 2-week project. Switch to PostgreSQL when many users write at the same time or data grows large. Only `DATABASE_URL` changes because SQLAlchemy hides the differences.

**What is an ORM / why SQLAlchemy?**
It maps tables to Python classes, so we write `Document(...)` instead of raw SQL, and it protects against SQL injection by using parameterised queries.

**Why `ON DELETE CASCADE`?**
Deleting a user (or a document) automatically deletes its dependent rows, so no orphan embeddings or documents are left. Tested in `test_deleting_user_cascades_to_everything`.

**Why store the password as a hash?**
If the database leaks, attackers still do not get the passwords. Hashes are salted (the same password gives different hashes) and slow on purpose.

**What does CI do?**
GitHub Actions runs the test suite on every push/pull request, so broken code is caught before it reaches `main`.

**What is Docker for?**
It packages the app with its exact dependencies so "works on my machine" becomes "works everywhere".
