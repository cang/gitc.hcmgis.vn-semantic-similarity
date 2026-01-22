from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from shared.schemas.text_corpus import (
    TextCorpusCreate,
    TextCorpusUpdate,
    TextCorpusOut,
    TextCorpusListOut,
)
from services.main_api.services import text_corpus as service
from services.main_api.services import text_semantic as semantic
from shared.db.session import SessionLocal

#SCORE_THRESHOLD = 0.8 # sẽ là tham số nhập hoặc cấu hình
SCORE_EXACTLY = 0.999

router = APIRouter(prefix="/corpus", tags=["TextCorpus"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TextCorpusOut)
def create(
    data: TextCorpusCreate,
    db: Session = Depends(get_db),
):
    text = data.content

    # Cần kiểm tra trùng trước khi xử lý , có thể kiểm tra trùng tuyệt đối
    dupResult = semantic.search(text)
    if dupResult.get('result')==0:
        return TextCorpusOut(id="embed-error", content="Không thể vector hóa văn bản")
    
    if dupResult.get('result') > 0  and len(dupResult.get('results')) > 0 and dupResult.get('results')[0].get('score')>=SCORE_EXACTLY:
        return TextCorpusOut(id="existed", content="Đã tồn tại")
    
    # Add vô vector database
    if not semantic.add(text):
        return TextCorpusOut(id="vectordb-error", content="Không thể thêm vô Vector database")
    
    # Add vô database
    return service.create_corpus(db, text)

@router.get("/{corpus_id}", response_model=TextCorpusOut)
def get(
    corpus_id: str,
    db: Session = Depends(get_db),
):
    corpus = service.get_corpus(db, corpus_id)
    if not corpus:
        raise HTTPException(404, "Corpus not found")
    return corpus

@router.get("/", response_model=TextCorpusListOut)
def list_(
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_corpus(
        db,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )

@router.put("/{corpus_id}", response_model=TextCorpusOut)
def update(
    corpus_id: str,
    data: TextCorpusUpdate,
    db: Session = Depends(get_db),
):
    corpus = service.update_corpus(db, corpus_id, data.content)
    if not corpus:
        raise HTTPException(404, "Corpus not found")
    return corpus

@router.delete("/{corpus_id}")
def delete(
    corpus_id: str,
    db: Session = Depends(get_db),
):
    ok = service.delete_corpus(db, corpus_id)
    if not ok:
        raise HTTPException(404, "Corpus not found")
    return {"deleted": True}

@router.post("/search")
def search(
    data: TextCorpusCreate,
    db: Session = Depends(get_db),
):
    text = data.content

    dupResult = semantic.search(text)
    if dupResult.get('result') > 0:
        for result in dupResult.get('results'):
            textCorpus = service.get_corpus(db, result.get('hash')) 
            if textCorpus:
                result.update({'text': textCorpus.content}) # cập nhật text từ hash 

    return dupResult
