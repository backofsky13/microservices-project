from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from .repository import init_demo, get_recommendations, add_recommendation, update_recommendation, delete_recommendation
from .auth import get_current_user
from typing import Optional
from pydantic import BaseModel

init_demo()
router = APIRouter(tags=["Recommendations"])

class AddRecRequest(BaseModel):
    product_id: str
    name: str
    category: str
    target_audience: list[str] = []

@router.get("/recommendations")
def list_recommendations(
    user_id: str,
    limit: int = Query(10),
    category: Optional[str] = None,
    user = Depends(get_current_user)
):
    return {
        "user_id": user_id,
        "recommendations": [r.dict() for r in get_recommendations(user_id, limit, category)]
    }

@router.post("/recommendations")
def post_recommendation(body: AddRecRequest, user = Depends(get_current_user)):
    if user.get("role") != "manager":
        raise HTTPException(403, "manager role required")
    rec = add_recommendation(body.dict())
    return {
        "status": "success",
        "message": "Товар добавлен в рекомендации",
        "recommendation_id": rec.recommendation_id
    }

@router.put("/recommendations/{recommendation_id}")
def put_recommendation(
    recommendation_id: str = Path(...),
    priority: int = Body(...),
    active: bool = Body(...),
    expires_at: Optional[str] = Body(None),
    user = Depends(get_current_user)
):
    if user.get("role") != "manager":
        raise HTTPException(403, "manager role required")
    patch = {"priority": priority, "active": active}
    if expires_at:
        from datetime import datetime
        patch["expires_at"] = datetime.fromisoformat(expires_at)
    try:
        update_recommendation(recommendation_id, patch)
        return {
            "status": "success",
            "message": "Товар рекомендации обновлен",
            "updated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z"
        }
    except KeyError:
        raise HTTPException(404, "not found")

@router.delete("/recommendations/{recommendation_id}")
def del_recommendation(recommendation_id: str, user = Depends(get_current_user)):
    if user.get("role") != "manager":
        raise HTTPException(403, "manager role required")
    try:
        delete_recommendation(recommendation_id)
        return {
            "status": "success",
            "message": "Рекомендация удалена",
            "deleted_recommendation_id": recommendation_id,
            "deleted_at": __import__("datetime").datetime.utcnow().isoformat() + "Z"
        }
    except KeyError:
        raise HTTPException(404, "not found")
