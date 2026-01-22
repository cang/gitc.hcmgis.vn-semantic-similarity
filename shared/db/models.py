from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime

from shared.db.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class TextCorpus(Base):
    __tablename__ = "text_corpus"

    id = Column(String, primary_key=True, index=True)
    content = Column(Text, nullable=False)

    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )