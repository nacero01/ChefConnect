from pydantic import BaseModel
from typing import Optional

class PantryItemRequest(BaseModel):
    item_name: str
    quantity: Optional[str] = None