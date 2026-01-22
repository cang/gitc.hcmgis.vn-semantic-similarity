from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from shared.core.config import settings
from shared.db.base import Base
from shared.db.session import engine
from services.main_api.api.home import router as home_router
from services.main_api.api.text_corpus import router as corpus_router
from sqlalchemy.exc import SQLAlchemyError

# DEV ONLY
if settings.APP_ENV == "dev":
    Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DES,
    version=settings.APP_VERSION
)

app.include_router(home_router)
app.include_router(corpus_router)
#app.include_router(document_router)

@app.get("/")
def home():
    return "Welcome API"

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
):
    return JSONResponse(
        status_code=503,
        content={"detail": "Database error"},
    )