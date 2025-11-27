from uuid import UUID
from datetime import datetime
from models import Recommendation, RecommendationType, CreateRecommendationRequest
from recommendation_repo import RecommendationRepo
from typing import List, Dict, Optional


class RecommendationService:
    def __init__(self):
        self.repo = RecommendationRepo()

    def get_personal_recommendations(self, user_id: UUID, limit: int = 10, category: Optional[str] = None) -> List[
        Dict]:
        """Получение персонализированных рекомендаций с вызовом вложенных функций"""

        # Вызов вложенной функции для получения истории пользователя
        user_history = self._get_user_history(user_id)

        # Вызов вложенной функции для генерации рекомендаций
        recommendations = self._generate_recommendations(user_history, limit, category)

        return recommendations

    def update_recommendations_based_on_order(self, user_id: UUID, order_data: dict) -> Dict:
        """Обновление рекомендаций на основе заказа"""
        products = order_data.get('products', [])

        # Вызов вложенной функции для обработки каждого товара
        for product in products:
            self._process_product_for_recommendations(user_id, product)

        return {"status": "success", "message": "Рекомендации обновлены на основе заказа"}

    def get_popular_recommendations(self, category: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Получение популярных рекомендаций"""
        popular_products = self.repo.get_popular_products(category, limit)

        recommendations = []
        for product in popular_products:
            recommendations.append({
                "product_id": product["product_id"],
                "name": product["product_name"],
                "category": product["category"],
                "price": product["price"],
                "discount_price": None,
                "score": product["rating"],
                "reason": "Популярный товар"
            })

        return recommendations

    # ВЛОЖЕННЫЕ ФУНКЦИИ (требование задания)
    def _get_user_history(self, user_id: UUID) -> List[Dict]:
        """Вложенная функция для получения истории пользователя"""
        # Заглушка для истории пользователя
        return [
            {"product_id": "prod_001", "category": "dairy", "rating": 5},
            {"product_id": "prod_003", "category": "beverages", "rating": 4}
        ]

    def _generate_recommendations(self, user_history: List[Dict], limit: int, category: Optional[str] = None) -> List[
        Dict]:
        """Вложенная функция для генерации рекомендаций"""
        popular_products = self.repo.get_popular_products(category, limit * 2)

        recommendations = []
        for product in popular_products:
            score = self._calculate_recommendation_score(product, user_history)

            recommendations.append({
                "product_id": product["product_id"],
                "name": product["product_name"],
                "category": product["category"],
                "price": product["price"],
                "discount_price": None,
                "score": score,
                "reason": self._get_recommendation_reason(score, product["category"])
            })

        return sorted(recommendations, key=lambda x: x["score"], reverse=True)[:limit]

    def _calculate_recommendation_score(self, product: Dict, user_history: List[Dict]) -> float:
        """Вложенная функция для расчета скоринга рекомендации"""
        base_score = product["rating"] * 0.6 + (product["orders_count"] / 1000) * 0.4

        # Учет предпочтений пользователя
        user_preference_boost = 0
        for history_item in user_history:
            if history_item["category"] == product["category"]:
                user_preference_boost += 0.2 * history_item["rating"]

        return min(base_score + user_preference_boost, 5.0)

    def _get_recommendation_reason(self, score: float, category: str) -> str:
        """Вложенная функция для определения причины рекомендации"""
        if score > 4.5:
            return f"Популярный товар в категории {category}"
        elif score > 4.0:
            return "На основе ваших предпочтений"
        else:
            return "Может вам понравиться"

    def _process_product_for_recommendations(self, user_id: UUID, product: Dict):
        """Вложенная функция для обработки товара для рекомендаций"""
        # В реальной системе здесь была бы логика обновления предпочтений
        pass