from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import Optional, List
from recommendation_service import RecommendationService
from models import CreateRecommendationRequest

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])

# Создаем экземпляр сервиса
recommendation_service = RecommendationService()

@router.get("/{user_id}")
def get_recommendations(
    user_id: UUID,
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = Query(None)
) -> List[dict]:
    """Получение персонализированных рекомендаций для пользователя"""
    try:
        return recommendation_service.get_personal_recommendations(user_id, limit, category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении рекомендаций: {str(e)}")

@router.post("/{user_id}/update-from-order")
def update_from_order(
    user_id: UUID,
    order_data: dict
):
    """Обновление рекомендаций на основе заказа пользователя"""
    try:
        return recommendation_service.update_recommendations_based_on_order(user_id, order_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении рекомендаций: {str(e)}")

@router.get("/")
def get_popular_recommendations(
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
) -> List[dict]:
    """Получение популярных рекомендаций"""
    try:
        return recommendation_service.get_popular_recommendations(category, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении популярных рекомендаций: {str(e)}")

@router.post("/")
def create_recommendation(request: CreateRecommendationRequest):
    """Создание рекомендации (для менеджеров)"""
    try:
        # В реальной системе здесь была бы проверка роли пользователя
        recommendation_data = request.dict()
        result = recommendation_service.repo.create_recommendation(recommendation_data)
        return {"status": "success", "recommendation_id": str(result.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании рекомендации: {str(e)}")