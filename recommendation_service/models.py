from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class RecommendationType(str, Enum):
    PERSONAL = 'personal'
    POPULAR = 'popular'
    CATEGORY = 'category'

class Recommendation(BaseModel):
    id: UUID
    user_id: UUID
    product_id: str
    product_name: str
    category: str
    price: float
    discount_price: Optional[float] = None
    recommendation_type: RecommendationType
    score: float
    reason: str
    created_at: datetime

class CreateRecommendationRequest(BaseModel):
    product_id: str
    product_name: str
    category: str
    price: float
    discount_price: Optional[float] = None