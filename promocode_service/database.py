from sqlalchemy import create_engine, Column, String, Float, DateTime, Enum, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/promocode_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PromocodeDB(Base):
    __tablename__ = "promocodes"

    id = Column(UUID, primary_key=True, default=uuid4)
    code = Column(String, unique=True, nullable=False)
    user_id = Column(UUID, nullable=False)
    discount_type = Column(Enum('percentage', 'fixed'), nullable=False)
    discount_value = Column(Float, nullable=False)
    min_order_amount = Column(Float, default=0.0)
    max_discount = Column(Float, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    usage_count = Column(Integer, default=0)
    max_usages = Column(Integer, default=1)
    status = Column(Enum('active', 'expired', 'used', 'inactive'), default='active')
    applicable_categories = Column(String)  # JSON string for categories
    created_at = Column(DateTime, default=datetime.now)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Создаем таблицы
Base.metadata.create_all(bind=engine)