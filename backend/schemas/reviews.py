from pydantic import BaseModel
from typing import Optional

class ReviewRequest(BaseModel):
    chef_id: int
    user_id: int
    rating: int
    comment: Optional[str] = None