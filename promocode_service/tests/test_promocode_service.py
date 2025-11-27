import pytest
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from promocode_service.promocode_repo import PromocodeRepo
from promocode_service.models import Promocode, DiscountType, ValidatePromocodeRequest, ApplyPromocodeRequest, \
    PromocodeStatus, CreatePromocodeRequest
from promocode_service.promocode_service import PromocodeService


@pytest.fixture
def mock_repo(monkeypatch):

    repo = PromocodeRepo()

    repo._promocodes = []
    return repo


@pytest.fixture
def service(mock_repo, monkeypatch):

    s = PromocodeService()
    monkeypatch.setattr(s, "repo", mock_repo)
    return s


def create_test_promocode(
    user_id=None,
    code="TEST10",
    expires_delta_days=1,
    discount_type=DiscountType.PERCENTAGE,
    discount_value=10,
    min_order_amount=100,
    usage_count=0,
    max_usages=1,
    applicable_categories=None
):
    return Promocode(
        id=uuid4(),
        code=code,
        user_id=user_id or uuid4(),
        discount_type=discount_type,
        discount_value=discount_value,
        min_order_amount=min_order_amount,
        max_discount=200,
        expires_at=datetime.now() + timedelta(days=expires_delta_days),
        usage_count=usage_count,
        max_usages=max_usages,
        status=PromocodeStatus.ACTIVE,
        applicable_categories=applicable_categories or [],
        created_at=datetime.now(),
    )




def test_validate_promocode_success(service, mock_repo):
    user_id = uuid4()
    promo = create_test_promocode(user_id=user_id)
    mock_repo._promocodes.append(promo)

    request = ValidatePromocodeRequest(
        promo_code=promo.code,
        user_id=user_id,
        order_amount=200,
        categories=[]
    )

    result = service.validate_promocode(request)

    assert result["valid"] is True
    assert result["discount_amount"] == 20   # 10% от 200


def test_validate_promocode_not_found(service):
    request = ValidatePromocodeRequest(
        promo_code="XXX",
        user_id=uuid4(),
        order_amount=100,
        categories=[]
    )
    result = service.validate_promocode(request)
    assert result["valid"] is False
    assert result["message"] == "Промокод не найден"


def test_validate_promocode_wrong_user(service, mock_repo):
    promo = create_test_promocode(user_id=uuid4())
    mock_repo._promocodes.append(promo)

    request = ValidatePromocodeRequest(
        promo_code=promo.code,
        user_id=uuid4(),
        order_amount=200,
        categories=[]
    )

    result = service.validate_promocode(request)
    assert result["valid"] is False
    assert result["message"] == "Промокод не доступен для данного пользователя"


def test_validate_promocode_expired(service, mock_repo):
    user_id = uuid4()
    promo = create_test_promocode(user_id=user_id, expires_delta_days=-1)
    mock_repo._promocodes.append(promo)

    request = ValidatePromocodeRequest(
        promo_code=promo.code,
        user_id=user_id,
        order_amount=200,
        categories=[]
    )

    result = service.validate_promocode(request)
    assert result["valid"] is False
    assert result["message"] == "Промокод не активен"


def test_validate_promocode_min_amount_fail(service, mock_repo):
    user_id = uuid4()
    promo = create_test_promocode(user_id=user_id, min_order_amount=500)
    mock_repo._promocodes.append(promo)

    request = ValidatePromocodeRequest(
        promo_code=promo.code,
        user_id=user_id,
        order_amount=100,
        categories=[]
    )

    result = service.validate_promocode(request)
    assert result["valid"] is False
    assert result["message"] == "Заказ не соответствует требованиям промокода"




def test_apply_promocode_success(service, mock_repo):
    user_id = uuid4()
    promo = create_test_promocode(user_id=user_id)
    mock_repo._promocodes.append(promo)

    req = ApplyPromocodeRequest(
        promo_code=promo.code,
        user_id=user_id,
        order_id=uuid4(),
        order_amount=200,
        final_amount=180
    )

    result = service.apply_promocode(req)

    assert result["status"] == "applied"
    assert result["discount_applied"] == 20
    assert result["usage_count"] == 1
    assert promo.usage_count == 1


def test_apply_promocode_turns_status_used(service, mock_repo):
    user_id = uuid4()
    promo = create_test_promocode(user_id=user_id, usage_count=0, max_usages=1)
    mock_repo._promocodes.append(promo)

    req = ApplyPromocodeRequest(
        promo_code=promo.code,
        user_id=user_id,
        order_id=uuid4(),
        order_amount=200,
        final_amount=180
    )

    result = service.apply_promocode(req)

    assert promo.status == PromocodeStatus.USED



def test_create_promocode_success(service, mock_repo):
    data = CreatePromocodeRequest(
        code="NEWYEAR",
        user_id=uuid4(),
        discount_type=DiscountType.FIXED,
        discount_value=100,
        expires_at=datetime.now() + timedelta(days=10),
        applicable_categories=[]
    )

    result = service.create_promocode(data)
    assert result["status"] == "created"
    assert mock_repo.get_by_code("NEWYEAR") is not None


def test_create_promocode_duplicate(service, mock_repo):
    p = create_test_promocode(code="DUPL")
    mock_repo._promocodes.append(p)

    data = CreatePromocodeRequest(
        code="DUPL",
        user_id=uuid4(),
        discount_type=DiscountType.FIXED,
        discount_value=100,
        expires_at=datetime.now() + timedelta(days=10),
        applicable_categories=[]
    )

    result = service.create_promocode(data)
    assert result["status"] == "error"



def test_get_user_promocodes(service, mock_repo):
    uid = uuid4()

    mock_repo._promocodes += [
        create_test_promocode(user_id=uid),
        create_test_promocode(user_id=uid),
        create_test_promocode(user_id=uuid4())
    ]

    result = service.get_user_promocodes(uid)
    assert len(result) == 2




def test_get_active_promocodes(service, mock_repo):
    mock_repo._promocodes += [
        create_test_promocode(expires_delta_days=1),      # active
        create_test_promocode(expires_delta_days=-1),     # expired
        create_test_promocode(expires_delta_days=5)       # active
    ]

    result = service.get_all_active_promocodes()
    assert len(result) == 2