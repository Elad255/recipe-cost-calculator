from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class IngredientCreate(BaseModel):
    name: str
    category: str
    unit: str
    price_per_unit: float


class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    price_per_unit: Optional[float] = None


class IngredientResponse(BaseModel):
    id: int
    name: str
    category: str
    unit: str
    price_per_unit: float
    created_at: datetime
    updated_at: datetime
    owner_id: int

    class Config:
        from_attributes = True