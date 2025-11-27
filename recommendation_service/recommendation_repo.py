from sqlalchemy.orm import Session
from database import get_db, RecommendationDB
from models import Recommendation, RecommendationType
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional


class RecommendationRepo:
    def __init__(self):
        self.db: Session = next(get_db())

    def get_user_recommendations(self, user_id: UUID, limit: int = 10, category: Optional[str] = None) -> List[
        Recommendation]:
        # Для простоты используем заглушку вместо реальной БД
        return self._get_demo_recommendations(user_id, limit, category)

    def create_recommendation(self, recommendation_data: dict) -> Recommendation:
        # Создаем демо-рекомендацию
        rec_id = uuid4()
        return Recommendation(
            id=rec_id,
            user_id=recommendation_data["user_id"],
            product_id=recommendation_data["product_id"],
            product_name=recommendation_data["product_name"],
            category=recommendation_data["category"],
            price=recommendation_data["price"],
            discount_price=recommendation_data.get("discount_price"),
            recommendation_type=recommendation_data["recommendation_type"],
            score=recommendation_data["score"],
            reason=recommendation_data["reason"],
            created_at=datetime.now()
        )

    def _get_demo_recommendations(self, user_id: UUID, limit: int, category: Optional[str]) -> List[Recommendation]:
        """Демо-рекомендации для тестирования"""
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
            }
        ]

        if category:
            demo_products = [p for p in demo_products if p['category'] == category]

        recommendations = []
        for product in demo_products[:limit]:
            recommendations.append(Recommendation(
                id=uuid4(),
                user_id=user_id,
                product_id=product["product_id"],
                product_name=product["product_name"],
                category=product["category"],
                price=product["price"],
                discount_price=product["discount_price"],
                recommendation_type=RecommendationType.PERSONAL,
                score=product["rating"],
                reason="Демо-рекомендация на основе популярности",
                created_at=datetime.now()
            ))

        return recommendations

    def get_popular_products(self, category: Optional[str] = None, limit: int = 20) -> List[dict]:
        """Получение популярных товаров"""
        popular_products = [
            {
                "product_id": "prod_001",
                "product_name": "Свежее молоко",
                "category": "dairy",
                "price": 89.99,
                "rating": 4.5,
                "orders_count": 1542
            },
            {
                "product_id": "prod_002",
                "product_name": "Хлеб белый",
                "category": "bakery",
                "price": 45.50,
                "rating": 4.7,
                "orders_count": 2034
            },
            {
                "product_id": "prod_003",
                "product_name": "Йогурт греческий",
                "category": "dairy",
                "price": 129.50,
                "rating": 4.8,
                "orders_count": 987
            }
        ]

        if category:
            popular_products = [p for p in popular_products if p['category'] == category]

        return popular_products[:limit]