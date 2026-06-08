from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional
from app.database import get_db
from app.models.models import User, Ingredient, PriceHistory
from app.schemas.price_history import PriceHistoryResponse, IngredientPriceHistory
from app.utils.deps import get_current_user
from app.utils.exceptions import IngredientNotFound, NotOwner

router = APIRouter(prefix="/price-history", tags=["Price History"])


@router.get("/ingredient/{ingredient_id}", response_model=IngredientPriceHistory)
def get_ingredient_price_history(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    ingredient = db.query(Ingredient).filter(
        Ingredient.id == ingredient_id
    ).first()

    if not ingredient:
        raise IngredientNotFound(ingredient_id)

    if ingredient.owner_id != current_user.id:
        raise NotOwner("ingredient")

    query = db.query(PriceHistory).filter(
        PriceHistory.ingredient_id == ingredient_id
    )

    if from_date:
        query = query.filter(PriceHistory.changed_at >= datetime.combine(from_date, datetime.min.time()))

    if to_date:
        query = query.filter(PriceHistory.changed_at <= datetime.combine(to_date, datetime.max.time()))

    query = query.order_by(PriceHistory.changed_at.desc())
    records = query.all()

    history = []
    for record in records:
        price_change = round(record.new_price - record.old_price, 2)
        change_percentage = round((price_change / record.old_price) * 100, 2) if record.old_price > 0 else 0

        history.append(PriceHistoryResponse(
            id=record.id,
            ingredient_id=record.ingredient_id,
            ingredient_name=ingredient.name,
            old_price=record.old_price,
            new_price=record.new_price,
            price_change=price_change,
            change_percentage=change_percentage,
            changed_at=record.changed_at
        ))

    return IngredientPriceHistory(
        ingredient_id=ingredient.id,
        ingredient_name=ingredient.name,
        current_price=ingredient.price_per_unit,
        history=history,
        total_changes=len(history)
    )


@router.get("/recent")
def get_recent_price_changes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50)
):
    records = db.query(PriceHistory).filter(
        PriceHistory.owner_id == current_user.id
    ).order_by(
        PriceHistory.changed_at.desc()
    ).limit(limit).all()

    result = []
    for record in records:
        price_change = round(record.new_price - record.old_price, 2)
        change_percentage = round((price_change / record.old_price) * 100, 2) if record.old_price > 0 else 0

        result.append({
            "id": record.id,
            "ingredient_id": record.ingredient_id,
            "ingredient_name": record.ingredient.name,
            "old_price": record.old_price,
            "new_price": record.new_price,
            "price_change": price_change,
            "change_percentage": change_percentage,
            "changed_at": record.changed_at.isoformat()
        })

    return {
        "total": len(result),
        "changes": result
    }