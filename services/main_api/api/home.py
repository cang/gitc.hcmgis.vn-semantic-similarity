from fastapi import APIRouter

router = APIRouter(prefix="", tags=["Home Page"])

@router.get("/")
def home():
    return "Xin chào, Tôi là API chuyên xử lý trùng lắp ngữ nghĩa của câu !!!"