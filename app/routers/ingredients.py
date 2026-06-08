from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from typing import List, Optional
from math import ceil
from app.database import get_db
from app.models.models import User, Ingredient, PriceHistory
from app.schemas.ingredient import IngredientCreate, IngredientUpdate, IngredientResponse
from app.schemas.common import PaginatedResponse
from app.utils.deps import get_current_user
from app.utils.exceptions import IngredientNotFound, DuplicateIngredient, NotOwner

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


@router.post("/", response_model=IngredientResponse)
def create_ingredient(
    ingredient_data: IngredientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Ingredient).filter(
        Ingredient.name == ingredient_data.name,
        Ingredient.owner_id == current_user.id
    ).first()
    if existing:
        raise DuplicateIngredient(ingredient_data.name)

    new_ingredient = Ingredient(
        name=ingredient_data.name,
        category=ingredient_data.category,
        unit=ingredient_data.unit,
        price_per_unit=ingredient_data.price_per_unit,
        owner_id=current_user.id
    )

    db.add(new_ingredient)
    db.commit()
    db.refresh(new_ingredient)

    return new_ingredient


@router.get("/", response_model=PaginatedResponse[IngredientResponse])
def get_ingredients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query(None, regex="^(name|category|price_per_unit|created_at)$"),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    query = db.query(Ingredient).filter(Ingredient.owner_id == current_user.id)

    if category:
        query = query.filter(Ingredient.category == category)

    if search:
        query = query.filter(Ingredient.name.ilike(f"%{search}%"))

    if min_price is not None:
        query = query.filter(Ingredient.price_per_unit >= min_price)

    if max_price is not None:
        query = query.filter(Ingredient.price_per_unit <= max_price)

    total = query.count()

    if sort_by:
        sort_column = getattr(Ingredient, sort_by)
        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

    offset = (page - 1) * size
    ingredients = query.offset(offset).limit(size).all()
    pages = ceil(total / size) if size > 0 else 0

    return PaginatedResponse(
        items=ingredients,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ingredient = db.query(Ingredient).filter(
        Ingredient.id == ingredient_id
    ).first()

    if not ingredient:
        raise IngredientNotFound(ingredient_id)

    if ingredient.owner_id != current_user.id:
        raise NotOwner("ingredient")

    return ingredient


@router.put("/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(
    ingredient_id: int,
    ingredient_data: IngredientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ingredient = db.query(Ingredient).filter(
        Ingredient.id == ingredient_id
    ).first()

    if not ingredient:
        raise IngredientNotFound(ingredient_id)

    if ingredient.owner_id != current_user.id:
        raise NotOwner("ingredient")

    if ingredient_data.price_per_unit is not None and ingredient_data.price_per_unit != ingredient.price_per_unit:
        price_record = PriceHistory(
            ingredient_id=ingredient.id,
            old_price=ingredient.price_per_unit,
            new_price=ingredient_data.price_per_unit,
            owner_id=current_user.id
        )
        db.add(price_record)

    if ingredient_data.name is not None:
        ingredient.name = ingredient_data.name
    if ingredient_data.category is not None:
        ingredient.category = ingredient_data.category
    if ingredient_data.unit is not None:
        ingredient.unit = ingredient_data.unit
    if ingredient_data.price_per_unit is not None:
        ingredient.price_per_unit = ingredient_data.price_per_unit

    db.commit()
    db.refresh(ingredient)

    return ingredient


@router.delete("/{ingredient_id}")
def delete_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ingredient = db.query(Ingredient).filter(
        Ingredient.id == ingredient_id
    ).first()

    if not ingredient:
        raise IngredientNotFound(ingredient_id)

    if ingredient.owner_id != current_user.id:
        raise NotOwner("ingredient")

    db.delete(ingredient)
    db.commit()

    return {"message": f"Ingredient '{ingredient.name}' deleted successfully"}