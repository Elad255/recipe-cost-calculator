from pydantic import BaseModel
from typing import Optional, List


class RecipeSummary(BaseModel):
    id: int
    name: str
    category: str
    servings: int
    selling_price: Optional[float] = None
    total_cost: float
    cost_per_serving: float
    profit_margin: Optional[float] = None


class AnalysisSummary(BaseModel):
    total_recipes: int
    recipes_with_ingredients: int
    average_cost_per_serving: float
    highest_cost_recipe: Optional[RecipeSummary] = None
    lowest_cost_recipe: Optional[RecipeSummary] = None
    highest_margin_recipe: Optional[RecipeSummary] = None
    lowest_margin_recipe: Optional[RecipeSummary] = None


class IngredientCostBreakdown(BaseModel):
    ingredient_id: int
    ingredient_name: str
    unit: str
    price_per_unit: float
    quantity: float
    cost: float
    percentage_of_total: float


class RecipeCostBreakdown(BaseModel):
    recipe_id: int
    recipe_name: str
    servings: int
    selling_price: Optional[float] = None
    total_cost: float
    cost_per_serving: float
    profit_margin: Optional[float] = None
    ingredients: List[IngredientCostBreakdown] = []