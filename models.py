from sqlalchemy import Column, Integer, String, Float
from database import Base, engine

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)

# Cria as tabelas no banco de dados (SQLite)
Base.metadata.create_all(bind=engine)
