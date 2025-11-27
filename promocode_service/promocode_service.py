from uuid import UUID
from datetime import datetime
from typing import Dict, List
from .models import (
    Promocode, PromocodeStatus, DiscountType,
    CreatePromocodeRequest, ValidatePromocodeRequest, ApplyPromocodeRequest
)
from .promocode_repo import PromocodeRepo


class PromocodeService:
    def __init__(self):
        self.repo = PromocodeRepo()

    def validate_promocode(self, request: ValidatePromocodeRequest) -> Dict:
        promocode = self.repo.get_by_code(request.promo_code)
        if not promocode:
            return {"valid": False, "message": "Промокод не найден"}

        if not self._check_user_eligibility(promocode, request.user_id):
            return {"valid": False, "message": "Промокод не доступен для данного пользователя"}

        if not self._check_promocode_status(promocode):
            return {"valid": False, "message": "Промокод не активен"}

        if not self._check_order_requirements(promocode, request.order_amount, request.categories):
            return {"valid": False, "message": "Заказ не соответствует требованиям промокода"}

        discount_amount = self._calculate_discount(promocode, request.order_amount)

        return {
            "valid": True,
            "promo_code": promocode.code,
            "discount_amount": discount_amount,
            "discount_percent": promocode.discount_value if promocode.discount_type == DiscountType.PERCENTAGE else None,
            "min_order_amount": promocode.min_order_amount,
            "max_discount": promocode.max_discount,
            "expires_at": promocode.expires_at.isoformat(),
            "applicable_categories": promocode.applicable_categories
        }

    def apply_promocode(self, request: ApplyPromocodeRequest) -> Dict:
        validation_result = self.validate_promocode(ValidatePromocodeRequest(
            promo_code=request.promo_code,
            user_id=request.user_id,
            order_amount=request.order_amount,
            categories=[]
        ))
        if not validation_result["valid"]:
            return validation_result

        promocode = self.repo.get_by_code(request.promo_code)
        promocode.usage_count += 1
        if promocode.usage_count >= promocode.max_usages:
            promocode.status = PromocodeStatus.USED

        self.repo.update_promocode(promocode)

        return {
            "status": "applied",
            "promo_code": promocode.code,
            "discount_applied": validation_result["discount_amount"],
            "usage_count": promocode.usage_count,
            "max_usages": promocode.max_usages,
            "final_amount": request.final_amount,
            "message": f"Промокод успешно применен! Скидка: {validation_result['discount_amount']} руб."
        }

    def create_promocode(self, request: CreatePromocodeRequest) -> Dict:
        existing_promocode = self.repo.get_by_code(request.code)
        if existing_promocode:
            return {"status": "error", "message": "Промокод с таким кодом уже существует"}

        promocode_data = request.dict()
        promocode = self.repo.create_promocode(promocode_data)

        return {
            "status": "created",
            "promo_code": promocode.code,
            "id": str(promocode.id),
            "message": "Промокод успешно создан"
        }

    def get_user_promocodes(self, user_id: UUID) -> List[Dict]:
        promocodes = self.repo.get_user_promocodes(user_id)
        result = []
        for promocode in promocodes:
            result.append({
                "code": promocode.code,
                "discount_type": promocode.discount_type,
                "discount_value": promocode.discount_value,
                "min_order_amount": promocode.min_order_amount,
                "max_discount": promocode.max_discount,
                "expires_at": promocode.expires_at.isoformat(),
                "usage_count": promocode.usage_count,
                "max_usages": promocode.max_usages,
                "status": promocode.status,
                "applicable_categories": promocode.applicable_categories
            })
        return result

    def get_all_active_promocodes(self) -> List[Dict]:
        active_promocodes = self.repo.get_active_promocodes()
        result = []
        for promocode in active_promocodes:
            result.append({
                "code": promocode.code,
                "discount_type": promocode.discount_type,
                "discount_value": promocode.discount_value,
                "min_order_amount": promocode.min_order_amount,
                "expires_at": promocode.expires_at.isoformat(),
                "usage_count": promocode.usage_count,
                "max_usages": promocode.max_usages
            })
        return result

    # --- вложенные функции ---
    def _check_user_eligibility(self, promocode: Promocode, user_id: UUID) -> bool:
        return promocode.user_id == user_id

    def _check_promocode_status(self, promocode: Promocode) -> bool:
        if promocode.status != PromocodeStatus.ACTIVE:
            return False
        if datetime.now() > promocode.expires_at:
            promocode.status = PromocodeStatus.EXPIRED
            self.repo.update_promocode(promocode)
            return False
        if promocode.usage_count >= promocode.max_usages:
            promocode.status = PromocodeStatus.USED
            self.repo.update_promocode(promocode)
            return False
        return True

    def _check_order_requirements(self, promocode: Promocode, order_amount: float, categories: List[str]) -> bool:
        if order_amount < promocode.min_order_amount:
            return False
        if promocode.applicable_categories and categories and not any(cat in promocode.applicable_categories for cat in categories):
            return False
        return True

    def _calculate_discount(self, promocode: Promocode, order_amount: float) -> float:
        if promocode.discount_type == DiscountType.PERCENTAGE:
            discount = order_amount * (promocode.discount_value / 100)
            if promocode.max_discount:
                discount = min(discount, promocode.max_discount)
            return round(discount, 2)
        else:
            return promocode.discount_value