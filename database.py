from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Choose database URL based on environment variable or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# For PostgreSQL, set DATABASE_URL to something like:
# postgresql+psycopg2://user:password@localhost/dbname

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
