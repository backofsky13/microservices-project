from sqlalchemy import create_engine, Column, String, Float, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/recommendation_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class RecommendationDB(Base):
    __tablename__ = "recommendations"

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, nullable=False)
    product_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    recommendation_type = Column(Enum('personal', 'popular', 'category'), nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Создаем таблицы
Base.metadata.create_all(bind=engine)