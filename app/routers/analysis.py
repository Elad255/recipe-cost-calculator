from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.models import User, Recipe
from app.schemas.analysis import (
    RecipeSummary, AnalysisSummary,
    IngredientCostBreakdown, RecipeCostBreakdown
)
from app.utils.deps import get_current_user
from app.utils.exceptions import RecipeNotFound, NotOwner

router = APIRouter(prefix="/recipes/analysis", tags=["Analysis"])


def calculate_recipe_summary(recipe):
    total_cost = 0
    for ri in recipe.recipe_ingredients:
        total_cost += ri.ingredient.price_per_unit * ri.quantity

    cost_per_serving = round(total_cost / recipe.servings, 2) if recipe.servings > 0 else 0

    profit_margin = None
    if recipe.selling_price and recipe.selling_price > 0:
        profit_margin = round(((recipe.selling_price - cost_per_serving) / recipe.selling_price) * 100, 2)

    return RecipeSummary(
        id=recipe.id,
        name=recipe.name,
        category=recipe.category,
        servings=recipe.servings,
        selling_price=recipe.selling_price,
        total_cost=round(total_cost, 2),
        cost_per_serving=cost_per_serving,
        profit_margin=profit_margin
    )


@router.get("/summary", response_model=AnalysisSummary)
def get_analysis_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipes = db.query(Recipe).filter(
        Recipe.owner_id == current_user.id
    ).all()

    if not recipes:
        return AnalysisSummary(
            total_recipes=0,
            recipes_with_ingredients=0,
            average_cost_per_serving=0
        )

    summaries = [calculate_recipe_summary(recipe) for recipe in recipes]

    recipes_with_ingredients = [s for s in summaries if s.total_cost > 0]

    average_cost = 0
    if recipes_with_ingredients:
        average_cost = round(
            sum(s.cost_per_serving for s in recipes_with_ingredients) / len(recipes_with_ingredients), 2
        )

    highest_cost = max(summaries, key=lambda s: s.cost_per_serving) if summaries else None
    lowest_cost = min(summaries, key=lambda s: s.cost_per_serving) if summaries else None

    recipes_with_margin = [s for s in summaries if s.profit_margin is not None]
    highest_margin = max(recipes_with_margin, key=lambda s: s.profit_margin) if recipes_with_margin else None
    lowest_margin = min(recipes_with_margin, key=lambda s: s.profit_margin) if recipes_with_margin else None

    return AnalysisSummary(
        total_recipes=len(summaries),
        recipes_with_ingredients=len(recipes_with_ingredients),
        average_cost_per_serving=average_cost,
        highest_cost_recipe=highest_cost,
        lowest_cost_recipe=lowest_cost,
        highest_margin_recipe=highest_margin,
        lowest_margin_recipe=lowest_margin
    )


@router.get("/low-margin")
def get_low_margin_recipes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    threshold: float = Query(30, ge=0, le=100)
):
    recipes = db.query(Recipe).filter(
        Recipe.owner_id == current_user.id
    ).all()

    summaries = [calculate_recipe_summary(recipe) for recipe in recipes]

    low_margin = [
        s for s in summaries
        if s.profit_margin is not None and s.profit_margin < threshold
    ]

    low_margin.sort(key=lambda s: s.profit_margin)

    return {
        "threshold": threshold,
        "count": len(low_margin),
        "recipes": low_margin
    }


@router.get("/cost-breakdown/{recipe_id}", response_model=RecipeCostBreakdown)
def get_cost_breakdown(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise RecipeNotFound(recipe_id)

    if recipe.owner_id != current_user.id:
        raise NotOwner("recipe")

    total_cost = 0
    ingredients_breakdown = []

    for ri in recipe.recipe_ingredients:
        cost = ri.ingredient.price_per_unit * ri.quantity
        total_cost += cost
        ingredients_breakdown.append({
            "ingredient_id": ri.ingredient.id,
            "ingredient_name": ri.ingredient.name,
            "unit": ri.ingredient.unit,
            "price_per_unit": ri.ingredient.price_per_unit,
            "quantity": ri.quantity,
            "cost": round(cost, 2),
            "percentage_of_total": 0
        })

    if total_cost > 0:
        for item in ingredients_breakdown:
            item["percentage_of_total"] = round((item["cost"] / total_cost) * 100, 2)

    cost_per_serving = round(total_cost / recipe.servings, 2) if recipe.servings > 0 else 0

    profit_margin = None
    if recipe.selling_price and recipe.selling_price > 0:
        profit_margin = round(((recipe.selling_price - cost_per_serving) / recipe.selling_price) * 100, 2)

    return RecipeCostBreakdown(
        recipe_id=recipe.id,
        recipe_name=recipe.name,
        servings=recipe.servings,
        selling_price=recipe.selling_price,
        total_cost=round(total_cost, 2),
        cost_per_serving=cost_per_serving,
        profit_margin=profit_margin,
        ingredients=ingredients_breakdown
    )