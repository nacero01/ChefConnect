from fastapi import APIRouter
from database import get_db_connection
from schemas.memberships import MembershipPlanRequest, ChefMembershipRequest

router = APIRouter(tags=["Memberships"])

@router.post("/membership-plans")
def create_membership_plan(data:MembershipPlanRequest):
    plan_name = data.plan_name
    price = data.price
    duration_months = data.duration_months

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    INSERT INTO MembershipPlan 
    (plan_name, price, duration_months)
    VALUES (%s, %s, %s)
    """

    cursor.execute(sql, (plan_name, price, duration_months))
    conn.commit()

    plan_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return {"message": "Membership plan created successfully!", "plan_id": plan_id}

@router.post("/chefs/{chef_id}/membership")
def add_chef_membership(chef_id: int, data:ChefMembershipRequest):
    plan_id = data. plan_id
    membership_type = data.membership_type
    start_date = data.start_date
    end_date = data.end_date

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    INSERT INTO ChefMembership 
    (chef_id, plan_id, membership_type, start_date, end_date)
    VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (chef_id, plan_id, membership_type, start_date, end_date))
    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Chef membership added successfully!"}