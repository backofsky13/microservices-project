from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class DiscountType(str, Enum):
    PERCENTAGE = 'percentage'
    FIXED = 'fixed'

class PromocodeStatus(str, Enum):
    ACTIVE = 'active'
    EXPIRED = 'expired'
    USED = 'used'
    INACTIVE = 'inactive'

class Promocode(BaseModel):
    id: UUID
    code: str
    user_id: UUID
    discount_type: DiscountType
    discount_value: float
    min_order_amount: float
    max_discount: Optional[float] = None
    expires_at: datetime
    usage_count: int
    max_usages: int
    status: PromocodeStatus
    applicable_categories: List[str]
    created_at: datetime

class CreatePromocodeRequest(BaseModel):
    code: str
    user_id: UUID
    discount_type: DiscountType
    discount_value: float
    min_order_amount: float = 0.0
    max_discount: Optional[float] = None
    expires_at: datetime
    max_usages: int = 1
    applicable_categories: List[str] = []

class ValidatePromocodeRequest(BaseModel):
    promo_code: str
    user_id: UUID
    order_amount: float
    categories: List[str] = []

class ApplyPromocodeRequest(BaseModel):
    promo_code: str
    user_id: UUID
    order_id: UUID
    order_amount: float
    final_amount: float