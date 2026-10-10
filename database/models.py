"""SQLAlchemy models = the tables from the project PDF (Users, Documents,
Embeddings) plus SearchHistory for the dashboard's "Recent Searches"."""
from datetime import datetime, timezone

from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, LargeBinary, String, Text,
)
from sqlalchemy.orm import relationship

from .db import Base


def _utcnow():
    """Naive UTC timestamp (works on SQLite and PostgreSQL)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    # Store a hash (passlib/bcrypt), NEVER the plain password.
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    documents = relationship(
        "Document", back_populates="owner", cascade="all, delete-orphan"
    )
    searches = relationship(
        "SearchHistory", back_populates="user", cascade="all, delete-orphan"
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)       # 'pdf' | 'image'
    file_size = Column(Integer, nullable=False, default=0)  # bytes
    category = Column(String(60), index=True)
    extracted_text = Column(Text)
    summary = Column(Text)
    tags = Column(Text)                                   # "python,certificate"
    upload_date = Column(DateTime, default=_utcnow)

    owner = relationship("User", back_populates="documents")
    embedding = relationship(
        "Embedding", back_populates="document", uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def tag_list(self):
        return [t.strip() for t in (self.tags or "").split(",") if t.strip()]


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"),
                         unique=True, nullable=False)
    dim = Column(Integer, nullable=False)
    vector = Column(LargeBinary, nullable=False)          # float32 bytes

    document = relationship("Document", back_populates="embedding")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    query = Column(String(500), nullable=False)
    result_count = Column(Integer, nullable=False, default=0)
    searched_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="searches")
