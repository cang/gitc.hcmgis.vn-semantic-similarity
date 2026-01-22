from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.core.config import settings

print(f"settings.database_url {settings.database_url}")
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
