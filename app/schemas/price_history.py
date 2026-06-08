from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class PriceHistoryResponse(BaseModel):
    id: int
    ingredient_id: int
    ingredient_name: str
    old_price: float
    new_price: float
    price_change: float
    change_percentage: float
    changed_at: datetime

    class Config:
        from_attributes = True


class IngredientPriceHistory(BaseModel):
    ingredient_id: int
    ingredient_name: str
    current_price: float
    history: List[PriceHistoryResponse]
    total_changes: int