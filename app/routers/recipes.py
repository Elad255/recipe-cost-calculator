from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from typing import List, Optional
from math import ceil
from app.database import get_db
from app.models.models import User, Recipe, Ingredient, RecipeIngredient
from app.schemas.recipe import (
    RecipeCreate, RecipeUpdate, RecipeResponse,
    RecipeIngredientAdd, RecipeIngredientResponse
)
from app.schemas.common import PaginatedResponse
from app.utils.deps import get_current_user
from app.utils.exceptions import NotOwner, RecipeNotFound, IngredientNotFound

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def build_recipe_response(recipe, db):
    ingredients_list = []
    total_cost = 0

    for ri in recipe.recipe_ingredients:
        ingredient = ri.ingredient
        cost = ingredient.price_per_unit * ri.quantity
        total_cost += cost
        ingredients_list.append(RecipeIngredientResponse(
            ingredient_id=ingredient.id,
            ingredient_name=ingredient.name,
            unit=ingredient.unit,
            price_per_unit=ingredient.price_per_unit,
            quantity=ri.quantity,
            cost=round(cost, 2)
        ))

    cost_per_serving = round(total_cost / recipe.servings, 2) if recipe.servings > 0 else 0

    profit_margin = None
    if recipe.selling_price and recipe.selling_price > 0:
        profit_margin = round(((recipe.selling_price - cost_per_serving) / recipe.selling_price) * 100, 2)

    return RecipeResponse(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        category=recipe.category,
        servings=recipe.servings,
        selling_price=recipe.selling_price,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        owner_id=recipe.owner_id,
        ingredients=ingredients_list,
        total_cost=round(total_cost, 2),
        cost_per_serving=cost_per_serving,
        profit_margin=profit_margin
    )


@router.post("/", response_model=RecipeResponse)
def create_recipe(
    recipe_data: RecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_recipe = Recipe(
        name=recipe_data.name,
        description=recipe_data.description,
        category=recipe_data.category,
        servings=recipe_data.servings,
        selling_price=recipe_data.selling_price,
        owner_id=current_user.id
    )

    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)

    return build_recipe_response(new_recipe, db)


@router.get("/", response_model=PaginatedResponse[RecipeResponse])
def get_recipes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(None, regex="^(name|category|servings|selling_price|created_at)$"),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    query = db.query(Recipe).filter(Recipe.owner_id == current_user.id)

    if category:
        query = query.filter(Recipe.category == category)

    if search:
        query = query.filter(Recipe.name.ilike(f"%{search}%"))

    total = query.count()

    if sort_by:
        sort_column = getattr(Recipe, sort_by)
        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

    offset = (page - 1) * size
    recipes = query.offset(offset).limit(size).all()
    pages = ceil(total / size) if size > 0 else 0

    return PaginatedResponse(
        items=[build_recipe_response(recipe, db) for recipe in recipes],
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise RecipeNotFound(recipe_id)

    if recipe.owner_id != current_user.id:
        raise NotOwner("recipe")

    return build_recipe_response(recipe, db)


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise RecipeNotFound(recipe_id)

    if recipe.owner_id != current_user.id:
        raise NotOwner("recipe")

    if recipe_data.name is not None:
        recipe.name = recipe_data.name
    if recipe_data.description is not None:
        recipe.description = recipe_data.description
    if recipe_data.category is not None:
        recipe.category = recipe_data.category
    if recipe_data.servings is not None:
        recipe.servings = recipe_data.servings
    if recipe_data.selling_price is not None:
        recipe.selling_price = recipe_data.selling_price

    db.commit()
    db.refresh(recipe)

    return build_recipe_response(recipe, db)


@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise RecipeNotFound(recipe_id)

    if recipe.owner_id != current_user.id:
        raise NotOwner("recipe")

    db.delete(recipe)
    db.commit()

    return {"message": f"Recipe '{recipe.name}' deleted successfully"}


@router.post("/{recipe_id}/ingredients", response_model=RecipeResponse)
def add_ingredient_to_recipe(
    recipe_id: int,
    data: RecipeIngredientAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise RecipeNotFound(recipe_id)
    if recipe.owner_id != current_user.id:
        raise NotOwner("recipe")

    ingredient = db.query(Ingredient).filter(
        Ingredient.id == data.ingredient_id
    ).first()
    if not ingredient:
        raise IngredientNotFound(data.ingredient_id)

    existing = db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe_id,
        RecipeIngredient.ingredient_id == data.ingredient_id
    ).first()

    if existing:
        existing.quantity = data.quantity
        db.commit()
        db.refresh(recipe)
        return build_recipe_response(recipe, db)

    new_ri = RecipeIngredient(
        recipe_id=recipe_id,
        ingredient_id=data.ingredient_id,
        quantity=data.quantity
    )

    db.add(new_ri)
    db.commit()
    db.refresh(recipe)

    return build_recipe_response(recipe, db)


@router.delete("/{recipe_id}/ingredients/{ingredient_id}", response_model=RecipeResponse)
def remove_ingredient_from_recipe(
    recipe_id: int,
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise RecipeNotFound(recipe_id)
    if recipe.owner_id != current_user.id:
        raise NotOwner("recipe")

    ri = db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe_id,
        RecipeIngredient.ingredient_id == ingredient_id
    ).first()

    if not ri:
        raise IngredientNotFound(ingredient_id)

    db.delete(ri)
    db.commit()
    db.refresh(recipe)

    return build_recipe_response(recipe, db)