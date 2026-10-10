"""Ready-made database functions for the other team members.

Member 2 (backend) calls these from the API routes.
Member 3 (AI) calls save_embedding / load_embeddings / update_document_ai.

Every document query is scoped by user_id on purpose: a logged-in user must
never be able to read another user's files (prevents IDOR attacks).
"""
from array import array
from collections import Counter
from typing import Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Document, Embedding, SearchHistory, User


# ----------------------------------------------------------------- users --
def create_user(db: Session, name: str, email: str, password_hash: str) -> User:
    user = User(name=name, email=email.strip().lower(), password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.strip().lower()).first()


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


# ------------------------------------------------------------- documents --
def add_document(
    db: Session, user_id: int, title: str, filename: str, filepath: str,
    file_type: str, file_size: int = 0, category: Optional[str] = None,
) -> Document:
    doc = Document(
        user_id=user_id, title=title, filename=filename, filepath=filepath,
        file_type=file_type, file_size=file_size, category=category,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def update_document_ai(
    db: Session, doc_id: int, *, extracted_text: Optional[str] = None,
    summary: Optional[str] = None, tags: Optional[Iterable[str]] = None,
    category: Optional[str] = None,
) -> Optional[Document]:
    """Store whatever the AI pipeline produced. Only given fields are changed."""
    doc = db.get(Document, doc_id)
    if doc is None:
        return None
    if extracted_text is not None:
        doc.extracted_text = extracted_text
    if summary is not None:
        doc.summary = summary
    if tags is not None:
        doc.tags = ",".join(t.strip() for t in tags if t and t.strip())
    if category is not None:
        doc.category = category
    db.commit()
    db.refresh(doc)
    return doc


def get_document(db: Session, doc_id: int, user_id: int) -> Optional[Document]:
    return (
        db.query(Document)
        .filter(Document.id == doc_id, Document.user_id == user_id)
        .first()
    )


def list_documents(
    db: Session, user_id: int, category: Optional[str] = None,
    limit: int = 50, offset: int = 0,
) -> List[Document]:
    q = db.query(Document).filter(Document.user_id == user_id)
    if category:
        q = q.filter(Document.category == category)
    return q.order_by(Document.upload_date.desc(), Document.id.desc()) \
            .offset(offset).limit(limit).all()


def get_documents_by_ids(db: Session, user_id: int, ids: Sequence[int]) -> List[Document]:
    """Fetch search hits, keeping the order of `ids` (best match first)."""
    if not ids:
        return []
    rows = (
        db.query(Document)
        .filter(Document.user_id == user_id, Document.id.in_(list(ids)))
        .all()
    )
    by_id = {d.id: d for d in rows}
    return [by_id[i] for i in ids if i in by_id]


def delete_document(db: Session, doc_id: int, user_id: int) -> bool:
    doc = get_document(db, doc_id, user_id)
    if doc is None:
        return False
    db.delete(doc)
    db.commit()
    return True


# ------------------------------------------------------------ embeddings --
def pack_vector(vector: Sequence[float]) -> bytes:
    """List/array of floats -> bytes (float32). Works with numpy arrays too."""
    return array("f", [float(x) for x in vector]).tobytes()


def unpack_vector(blob: bytes) -> List[float]:
    arr = array("f")
    arr.frombytes(blob)
    return arr.tolist()


def save_embedding(db: Session, doc_id: int, vector: Sequence[float]) -> Embedding:
    """Insert or replace the embedding of a document."""
    blob = pack_vector(vector)
    emb = db.query(Embedding).filter(Embedding.document_id == doc_id).first()
    if emb is None:
        emb = Embedding(document_id=doc_id, dim=len(vector), vector=blob)
        db.add(emb)
    else:
        emb.dim, emb.vector = len(vector), blob
    db.commit()
    db.refresh(emb)
    return emb


def load_embeddings(db: Session, user_id: Optional[int] = None) -> List[Tuple[int, List[float]]]:
    """[(document_id, vector), ...] - used to (re)build the FAISS index."""
    q = db.query(Embedding.document_id, Embedding.vector).join(
        Document, Document.id == Embedding.document_id
    )
    if user_id is not None:
        q = q.filter(Document.user_id == user_id)
    return [(doc_id, unpack_vector(blob)) for doc_id, blob in q.all()]


# -------------------------------------------------------- search history --
def log_search(db: Session, user_id: int, query: str, result_count: int = 0) -> SearchHistory:
    row = SearchHistory(user_id=user_id, query=query.strip()[:500], result_count=result_count)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def recent_searches(db: Session, user_id: int, limit: int = 5) -> List[SearchHistory]:
    return (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == user_id)
        .order_by(SearchHistory.searched_at.desc(), SearchHistory.id.desc())
        .limit(limit).all()
    )


# ------------------------------------------------------------- dashboard --
def dashboard_stats(db: Session, user_id: int) -> dict:
    """Everything the dashboard page shows, in one call."""
    docs = db.query(Document).filter(Document.user_id == user_id)

    total = docs.count()
    pdfs = docs.filter(Document.file_type == "pdf").count()
    images = docs.filter(Document.file_type == "image").count()
    storage = (
        db.query(func.coalesce(func.sum(Document.file_size), 0))
        .filter(Document.user_id == user_id).scalar()
    )

    categories = dict(
        db.query(Document.category, func.count(Document.id))
        .filter(Document.user_id == user_id, Document.category.isnot(None))
        .group_by(Document.category).all()
    )

    tag_counter: Counter = Counter()
    for (tags,) in db.query(Document.tags).filter(
        Document.user_id == user_id, Document.tags.isnot(None)
    ):
        tag_counter.update(t for t in tags.split(",") if t)

    return {
        "total_files": total,
        "pdfs": pdfs,
        "images": images,
        "storage_used_bytes": int(storage or 0),
        "categories": categories,
        "ai_tags_total": sum(tag_counter.values()),
        "top_tags": tag_counter.most_common(8),
        "recent_uploads": [
            {"id": d.id, "title": d.title, "upload_date": d.upload_date.isoformat()}
            for d in list_documents(db, user_id, limit=5)
        ],
        "recent_searches": [
            {"query": s.query, "result_count": s.result_count,
             "searched_at": s.searched_at.isoformat()}
            for s in recent_searches(db, user_id, limit=5)
        ],
    }
