from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


from shared.db.session import SessionLocal
from shared.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentOut,
    DocumentListOut
)
from services.main_api.services import document as service

router = APIRouter(prefix="/documents", tags=["documents"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=DocumentListOut)
def list_docs(
    keyword: str | None = Query(None, description="Search keyword"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        return service.list_documents(
            db,
            keyword=keyword,
            page=page,
            page_size=page_size,
    )        
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable"
        )

@router.post("/", response_model=DocumentOut)
def create(doc: DocumentCreate, db: Session = Depends(get_db)):
    return service.create_document(db, doc.content)

@router.get("/{doc_id}", response_model=DocumentOut)
def read(doc_id: str, db: Session = Depends(get_db)):
    document = service.get_document(db, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.put("/{doc_id}", response_model=DocumentOut)
def update(doc_id: str, doc: DocumentUpdate, db: Session = Depends(get_db)):
    document = service.update_document(db, doc_id, doc.content)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/{doc_id}")
def delete(doc_id: str, db: Session = Depends(get_db)):
    ok = service.delete_document(db, doc_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": True}
