from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import User, Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientUpdate, IngredientResponse
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


@router.get("/", response_model=List[IngredientResponse])
def get_ingredients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ingredients = db.query(Ingredient).filter(
        Ingredient.owner_id == current_user.id
    ).all()

    return ingredients


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