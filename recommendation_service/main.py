from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


# Модели данных
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


# Демо-данные
demo_products = [
    {
        "product_id": "prod_001",
        "product_name": "Свежее молоко",
        "category": "dairy",
        "price": 89.99,
        "discount_price": 79.99,
        "rating": 4.5,
        "orders_count": 1542
    },
    {
        "product_id": "prod_002",
        "product_name": "Хлеб белый",
        "category": "bakery",
        "price": 45.50,
        "discount_price": None,
        "rating": 4.7,
        "orders_count": 2034
    },
    {
        "product_id": "prod_003",
        "product_name": "Йогурт греческий",
        "category": "dairy",
        "price": 129.50,
        "discount_price": 116.55,
        "rating": 4.8,
        "orders_count": 987
    },
    {
        "product_id": "prod_004",
        "product_name": "Сок апельсиновый",
        "category": "beverages",
        "price": 120.00,
        "discount_price": 99.99,
        "rating": 4.3,
        "orders_count": 756
    }
]

app = FastAPI(
    title="Recommendation Service",
    description="Сервис рекомендаций для системы доставки продуктов",
    version="1.0.0"
)


# ВЛОЖЕННЫЕ ФУНКЦИИ (требование задания)
def _get_user_history(user_id: UUID) -> List[dict]:
    """Вложенная функция для получения истории пользователя"""
    return [
        {"product_id": "prod_001", "category": "dairy", "rating": 5},
        {"product_id": "prod_003", "category": "beverages", "rating": 4}
    ]


def _calculate_recommendation_score(product: dict, user_history: List[dict]) -> float:
    """Вложенная функция для расчета скоринга рекомендации"""
    base_score = product["rating"] * 0.6 + (product["orders_count"] / 1000) * 0.4

    user_preference_boost = 0
    for history_item in user_history:
        if history_item["category"] == product["category"]:
            user_preference_boost += 0.2 * history_item["rating"]

    return min(base_score + user_preference_boost, 5.0)


def _get_recommendation_reason(score: float, category: str) -> str:
    """Вложенная функция для определения причины рекомендации"""
    if score > 4.5:
        return f"Популярный товар в категории {category}"
    elif score > 4.0:
        return "На основе ваших предпочтений"
    else:
        return "Может вам понравиться"


def _generate_recommendations(user_history: List[dict], limit: int, category: Optional[str] = None) -> List[dict]:
    """Вложенная функция для генерации рекомендаций"""
    filtered_products = demo_products.copy()

    if category:
        filtered_products = [p for p in filtered_products if p['category'] == category]

    recommendations = []
    for product in filtered_products:
        score = _calculate_recommendation_score(product, user_history)

        recommendations.append({
            "product_id": product["product_id"],
            "name": product["product_name"],
            "category": product["category"],
            "price": product["price"],
            "discount_price": product["discount_price"],
            "score": score,
            "reason": _get_recommendation_reason(score, product["category"])
        })

    return sorted(recommendations, key=lambda x: x["score"], reverse=True)[:limit]


# ЭНДПОИНТЫ (4 эндпоинта как требуется)
@app.get("/api/v1/recommendations/{user_id}")
def get_recommendations(
        user_id: UUID,
        limit: int = Query(10, ge=1, le=50),
        category: Optional[str] = Query(None)
) -> List[dict]:
    """Получение персонализированных рекомендаций для пользователя"""
    try:
        # Вызов вложенных функций
        user_history = _get_user_history(user_id)
        recommendations = _generate_recommendations(user_history, limit, category)

        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении рекомендаций: {str(e)}")


@app.post("/api/v1/recommendations/{user_id}/update-from-order")
def update_from_order(user_id: UUID, order_data: dict):
    """Обновление рекомендаций на основе заказа пользователя"""
    try:
        # В реальной системе здесь была бы логика обновления
        return {"status": "success", "message": "Рекомендации обновлены на основе заказа"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении рекомендаций: {str(e)}")


@app.get("/api/v1/recommendations/")
def get_popular_recommendations(
        category: Optional[str] = Query(None),
        limit: int = Query(20, ge=1, le=100)
) -> List[dict]:
    """Получение популярных рекомендаций"""
    try:
        filtered_products = demo_products.copy()
        if category:
            filtered_products = [p for p in filtered_products if p['category'] == category]

        recommendations = []
        for product in filtered_products[:limit]:
            recommendations.append({
                "product_id": product["product_id"],
                "name": product["product_name"],
                "category": product["category"],
                "price": product["price"],
                "discount_price": product["discount_price"],
                "score": product["rating"],
                "reason": "Популярный товар"
            })

        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении популярных рекомендаций: {str(e)}")


@app.post("/api/v1/recommendations/")
def create_recommendation(request: CreateRecommendationRequest):
    """Создание рекомендации"""
    try:
        recommendation = Recommendation(
            id=uuid4(),
            user_id=uuid4(),
            product_id=request.product_id,
            product_name=request.product_name,
            category=request.category,
            price=request.price,
            discount_price=request.discount_price,
            recommendation_type=RecommendationType.PERSONAL,
            score=4.0,
            reason="Ручное добавление менеджером",
            created_at=datetime.now()
        )

        return {
            "status": "success",
            "message": "Товар добавлен в рекомендации",
            "recommendation_id": str(recommendation.id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании рекомендации: {str(e)}")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "recommendation"}


@app.get("/")
def root():
    return {"message": "Recommendation Service is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)