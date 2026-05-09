from pydantic import BaseModel
from typing import Optional

class BookingRequest(BaseModel):
    chef_id: int
    user_id: int
    booking_date: str
    booking_time: str
    customer_requests: Optional[str] = None

class BookingStatusRequest(BaseModel):
    status: str

class BookingIngredientRequest(BaseModel):
    ingredient_name: str
    quantity: Optional[str] = None
    notes: Optional[str] = None