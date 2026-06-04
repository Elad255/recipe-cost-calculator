from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class RecipeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    servings: int = 1
    selling_price: Optional[float] = None


class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    servings: Optional[int] = None
    selling_price: Optional[float] = None


class RecipeIngredientAdd(BaseModel):
    ingredient_id: int
    quantity: float


class RecipeIngredientResponse(BaseModel):
    ingredient_id: int
    ingredient_name: str
    unit: str
    price_per_unit: float
    quantity: float
    cost: float

    class Config:
        from_attributes = True


class RecipeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: str
    servings: int
    selling_price: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    owner_id: int
    ingredients: List[RecipeIngredientResponse] = []
    total_cost: float = 0
    cost_per_serving: float = 0
    profit_margin: Optional[float] = None

    class Config:
        from_attributes = True