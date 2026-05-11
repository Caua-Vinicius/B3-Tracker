from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

import os

# Garante que a pasta data exista para persistência no Docker
os.makedirs("data", exist_ok=True)
DATABASE_URL = "sqlite:///data/portfolio.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
