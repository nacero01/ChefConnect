from pydantic import BaseModel
from typing import Optional

class ChefProfileRequest(BaseModel):
    bio: Optional[str] = None
    specialty: Optional[str] = None

class AvailabilityRequest(BaseModel):
    day_of_week: str
    start_time: str
    end_time: str