from sqlalchemy import create_engine, text
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

def run_migrations():
    """
    Aplica migrações incrementais no schema do SQLite sem Alembic.
    Cada bloco é idempotente: falha silenciosamente se a coluna já existir.
    """
    with engine.connect() as conn:
        # v1 → v2: adiciona preço médio de compra
        try:
            conn.execute(text("ALTER TABLE assets ADD COLUMN avg_price FLOAT DEFAULT 0.0"))
            conn.commit()
        except Exception:
            pass  # Coluna já existe — seguro ignorar

run_migrations()
