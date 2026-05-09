from pydantic import BaseModel
from typing import Optional

class MembershipPlanRequest(BaseModel):
    plan_name: str
    price: float
    duration_months: int

class ChefMembershipRequest(BaseModel):
    plan_id: int
    membership_type: Optional[str] = None
    start_date: str
    end_date: str