from sqlalchemy.orm import Session
from shared.db.models import Document

from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from shared.utils.hashing import hash_text

def safe_commit(db: Session):
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error"
        )
    
def create_document(db: Session, content: str) -> Document:
    doc_id = hash_text(content)

    document = Document(id=doc_id, content=content)
    db.add(document)
    safe_commit(db)
    db.refresh(document)
    return document

def get_document(db: Session, doc_id: str) -> Document | None:
    return db.query(Document).filter(Document.id == doc_id).first()

def update_document(db: Session, doc_id: str, content: str) -> Document | None:
    document = get_document(db, doc_id)
    if not document:
        return None

    document.content = content
    safe_commit(db)
    db.refresh(document)
    return document

def delete_document(db: Session, doc_id: str) -> bool:
    document = get_document(db, doc_id)
    if not document:
        return False

    db.delete(document)
    safe_commit(db)
    return True

def list_documents(
    db: Session,
    *,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    query = db.query(Document)

    if keyword:
        query = query.filter(Document.content.ilike(f"%{keyword}%"))

    total = query.count()

    items = (
        query
        .order_by(Document.created_at.desc())
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

