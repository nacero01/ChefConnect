from fastapi import APIRouter
from database import get_db_connection

router = APIRouter(tags=["Pantry"])

@router.post("/users/{user_id}/pantry")
def add_user_pantry_item(
    user_id: int,
    item_name: str,
    quantity: str = None
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    INSERT INTO ClientPantry 
    (user_id, item_name, quantity)
    VALUES (%s, %s, %s)
    """

    cursor.execute(sql, (user_id, item_name, quantity))
    conn.commit()

    pantry_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return {"message": "Item added to pantry successfully!", "pantry_id": pantry_id}

@router.get("/users/{user_id}/pantry")
def get_user_pantry_items(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT *
    FROM ClientPantry
    WHERE user_id = %s
    """

    cursor.execute(sql, (user_id,))
    pantry_items = cursor.fetchall()

    cursor.close()
    conn.close()
    return {"pantry_items": pantry_items}