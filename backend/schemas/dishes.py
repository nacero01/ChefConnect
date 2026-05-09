from pydantic import BaseModel
from typing import Optional

class DishRequest(BaseModel):
    dish_name: str
    description: Optional[str] = None
    price: float

class DishUpdateRequest(BaseModel):
    dish_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None