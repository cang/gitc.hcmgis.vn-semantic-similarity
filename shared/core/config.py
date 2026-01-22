from pydantic_settings import BaseSettings, SettingsConfigDict
from shared.enum.run_mode import RunMode

class Settings(BaseSettings):
    APP_ENV: str = "dev"
    APP_RUN_MODE: RunMode
    APP_NAME: str = "Semantic Search API"

    APP_TITLE: str = "Semantic Search API - Kho Văn Bản"
    APP_DES: str = "API tìm kiếm ngữ nghĩa trên kho văn bản lớn. Hỗ trợ thêm văn bản và tìm kiếm tương đồng."
    APP_VERSION: str = "1.0.0"

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str = "semantic-documents"
    DB_USER: str
    DB_PASSWORD: str

    EMBED_HOST: str = "nginx"
    EMBED_PORT: int = 8002

    QDRAN_HOST: str = "qdrant"
    QDRAN_PORT: int = 6333

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    #model_config = SettingsConfigDict(env_file=".env", extra="ignore")


    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )    

    class Config:
        env_file = ".env"

settings = Settings()
