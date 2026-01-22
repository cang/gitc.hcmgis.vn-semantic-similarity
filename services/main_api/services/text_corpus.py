from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from shared.db.models import TextCorpus
from shared.utils.hashing import hash_text

def safe_commit(db: Session):
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Database error",
        )

def create_corpus(db: Session, content: str) -> TextCorpus:
    corpus = TextCorpus(
        id=hash_text(content),
        content=content,
    )
    db.add(corpus)
    safe_commit(db)
    db.refresh(corpus)
    return corpus

def get_corpus(db: Session, corpus_id: str) -> TextCorpus | None:
    return (
        db.query(TextCorpus)
        .filter(TextCorpus.id == corpus_id)
        .first()
    )

def list_corpus(
    db: Session,
    *,
    keyword: str | None,
    page: int,
    page_size: int,
):
    query = db.query(TextCorpus)

    if keyword:
        query = query.filter(
            TextCorpus.content.ilike(f"%{keyword}%")
        )

    total = query.count()

    items = (
        query
        .order_by(TextCorpus.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }

def update_corpus(
    db: Session,
    corpus_id: str,
    content: str,
) -> TextCorpus | None:
    corpus = get_corpus(db, corpus_id)
    if not corpus:
        return None

    corpus.content = content
    safe_commit(db)
    db.refresh(corpus)
    return corpus

def delete_corpus(db: Session, corpus_id: str) -> bool:
    corpus = get_corpus(db, corpus_id)
    if not corpus:
        return False

    db.delete(corpus)
    safe_commit(db)
    return True


