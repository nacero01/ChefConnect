from fastapi import APIRouter
from database import get_db_connection
import mysql.connector

router = APIRouter(tags=["Favorites"])

@router.post("/users/{user_id}/favorites/{chef_id}")
def add_favorite_chef(user_id: int, chef_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    INSERT INTO FavoriteChef (user_id, chef_id)
    VALUES (%s, %s)
    """

    try:
        cursor.execute(sql, (user_id, chef_id))
        conn.commit()
    except mysql.connector.IntegrityError:
        cursor.close()
        conn.close()
        return {"message": "This chef is already in your favorites."}

    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Chef added to favorites successfully!"}

@router.get("/users/{user_id}/favorites")
def get_favorite_chefs(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT 
        c.chef_id,
        u.username,
        c.specialty,
        c.rating
    FROM UserFavoriteChef f
    JOIN Chef c ON f.chef_id = c.chef_id
    JOIN User u ON c.user_id = u.user_id
    WHERE f.user_id = %s
    """

    cursor.execute(sql, (user_id,))
    favorite_chefs = cursor.fetchall()

    cursor.close()
    conn.close()
    return {"favorite_chefs": favorite_chefs}

@router.delete("/users/{user_id}/favorites/{chef_id}")
def remove_favorite_chef(user_id: int, chef_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    DELETE FROM FavoriteChef
    WHERE user_id = %s AND chef_id = %s
    """

    cursor.execute(sql, (user_id, chef_id))
    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Chef removed from favorites successfully!"}