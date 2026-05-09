from fastapi import APIRouter
from database import get_db_connection

router = APIRouter(tags=["Memberships"])

@router.post("/membership-plans")
def create_membership_plan(
    plan_name: str,
    price: float,
    duration_months: int
):
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
def add_chef_membership(
    chef_id: int,
    plan_id: int,
    membership_type: str = None,
    start_date: str = None,
    end_date: str = None
):
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