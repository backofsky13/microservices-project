from uuid import UUID
from datetime import datetime
from typing import List, Optional
from .models import Promocode, PromocodeStatus, DiscountType


class PromocodeRepo:
    def __init__(self):
        # Демо-данные вместо реальной БД
        self._promocodes: List[Promocode] = self._create_demo_promocodes()

    def get_by_code(self, code: str) -> Optional[Promocode]:
        for promo in self._promocodes:
            if promo.code == code:
                return promo
        return None

    def get_user_promocodes(self, user_id: UUID) -> List[Promocode]:
        return [p for p in self._promocodes if p.user_id == user_id]

    def create_promocode(self, promocode_data: dict) -> Promocode:
        from uuid import uuid4

        promocode = Promocode(
            id=uuid4(),
            usage_count=0,
            status=PromocodeStatus.ACTIVE,
            created_at=datetime.now(),
            **promocode_data
        )
        self._promocodes.append(promocode)
        return promocode

    def update_promocode(self, promocode: Promocode) -> Promocode:
        return promocode

    def get_active_promocodes(self) -> List[Promocode]:
        now = datetime.now()
        return [
            p for p in self._promocodes
            if p.status == PromocodeStatus.ACTIVE and p.expires_at > now
        ]

    def _create_demo_promocodes(self) -> List[Promocode]:
        from uuid import UUID

        demo_user_id = UUID('12345678-1234-1234-1234-123456789012')

        return [
            Promocode(
                id=UUID('11111111-1111-1111-1111-111111111111'),
                code="WELCOME10",
                user_id=demo_user_id,
                discount_type=DiscountType.PERCENTAGE,
                discount_value=10,
                min_order_amount=500.0,
                max_discount=200.0,
                expires_at=datetime(2024, 12, 31, 23, 59, 59),
                usage_count=0,
                max_usages=1,
                status=PromocodeStatus.ACTIVE,
                applicable_categories=["dairy", "bakery", "beverages"],
                created_at=datetime.now()
            ),
            Promocode(
                id=UUID('22222222-2222-2222-2222-222222222222'),
                code="SUMMER25",
                user_id=demo_user_id,
                discount_type=DiscountType.PERCENTAGE,
                discount_value=25,
                min_order_amount=1000.0,
                max_discount=500.0,
                expires_at=datetime(2024, 8, 31, 23, 59, 59),
                usage_count=1,
                max_usages=5,
                status=PromocodeStatus.ACTIVE,
                applicable_categories=["dairy", "meat", "fruits"],
                created_at=datetime.now()
            ),
            Promocode(
                id=UUID('33333333-3333-3333-3333-333333333333'),
                code="FREESHIP",
                user_id=demo_user_id,
                discount_type=DiscountType.FIXED,
                discount_value=150.0,
                min_order_amount=800.0,
                max_discount=None,
                expires_at=datetime(2024, 6, 30, 23, 59, 59),
                usage_count=2,
                max_usages=3,
                status=PromocodeStatus.ACTIVE,
                applicable_categories=[],
                created_at=datetime.now()
            )
        ]