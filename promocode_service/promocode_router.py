from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from models import CreatePromocodeRequest, ValidatePromocodeRequest, ApplyPromocodeRequest
from promocode_service import PromocodeService

router = APIRouter(prefix="/api/v1/promocodes", tags=["promocodes"])

# Создаем экземпляр сервиса
promocode_service = PromocodeService()


@router.post("/validate")
def validate_promocode(request: ValidatePromocodeRequest):
    """Валидация промокода"""
    try:
        return promocode_service.validate_promocode(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при валидации промокода: {str(e)}")


@router.post("/apply")
def apply_promocode(request: ApplyPromocodeRequest):
    """Применение промокода к заказу"""
    try:
        return promocode_service.apply_promocode(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при применении промокода: {str(e)}")


@router.post("/")
def create_promocode(request: CreatePromocodeRequest):
    """Создание нового промокода"""
    try:
        return promocode_service.create_promocode(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании промокода: {str(e)}")


@router.get("/user/{user_id}")
def get_user_promocodes(user_id: UUID):
    """Получение промокодов пользователя"""
    try:
        return promocode_service.get_user_promocodes(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении промокодов: {str(e)}")


@router.get("/active")
def get_active_promocodes():
    """Получение всех активных промокодов"""
    try:
        return promocode_service.get_all_active_promocodes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении активных промокодов: {str(e)}")


@router.get("/{promo_code}")
def get_promocode_info(promo_code: str):
    """Получение информации о промокоде"""
    try:
        promocode = promocode_service.repo.get_by_code(promo_code)
        if not promocode:
            raise HTTPException(status_code=404, detail="Промокод не найден")

        return {
            "code": promocode.code,
            "discount_type": promocode.discount_type,
            "discount_value": promocode.discount_value,
            "min_order_amount": promocode.min_order_amount,
            "max_discount": promocode.max_discount,
            "expires_at": promocode.expires_at.isoformat(),
            "usage_count": promocode.usage_count,
            "max_usages": promocode.max_usages,
            "status": promocode.status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении информации о промокоде: {str(e)}")