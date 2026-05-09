from fastapi import APIRouter
from database import get_db_connection

router = APIRouter(tags=["Dishes"])

@router.post("/chefs/{chef_id}/dishes")
def add_chef_dish(
    chef_id: int,
    dish_name: str,
    description: str = None,
    price: float = None
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    INSERT INTO Dish 
    (chef_id, dish_name, description, price)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(sql, (chef_id, dish_name, description, price))
    conn.commit()

    dish_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return {"message": "Dish added to chef's menu successfully!", "dish_id": dish_id}

@router.get("/chefs/{chef_id}/dishes")
def get_chef_dishes(chef_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT *
    FROM Dish
    WHERE chef_id = %s
    """

    cursor.execute(sql, (chef_id,))
    dishes = cursor.fetchall()

    cursor.close()
    conn.close()
    return {"dishes": dishes}

@router.put("/dishes/{dish_id}")
def update_chef_dish(
    dish_id: int,
    dish_name: str = None,
    description: str = None,
    price: float = None
):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if dish_name is not None:
        cursor.execute("UPDATE Dish SET dish_name = %s WHERE dish_id = %s", (dish_name, dish_id))
    if description is not None:
        cursor.execute("UPDATE Dish SET description = %s WHERE dish_id = %s", (description, dish_id))
    if price is not None:
        cursor.execute("UPDATE Dish SET price = %s WHERE dish_id = %s", (price, dish_id))
    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Dish updated successfully!"}

@router.delete("/dishes/{dish_id}")
def delete_chef_dish(dish_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    DELETE FROM Dish
    WHERE dish_id = %s
    """

    cursor.execute(sql, (dish_id,))
    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Dish deleted successfully!"}