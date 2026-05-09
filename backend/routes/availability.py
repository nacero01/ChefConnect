from fastapi import APIRouter
from database import get_db_connection

router = APIRouter(tags=["Availability"])

@router.put("/availability/{availability_id}")
def update_chef_availability(
    availability_id: int,
    day_of_week: str = None,
    start_time: str = None,
    end_time: str = None
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if day_of_week is not None:
        cursor.execute("UPDATE ChefAvailability SET day_of_week = %s WHERE availability_id = %s", (day_of_week, availability_id))
    if start_time is not None:
        cursor.execute("UPDATE ChefAvailability SET start_time = %s WHERE availability_id = %s", (start_time, availability_id))
    if end_time is not None:
        cursor.execute("UPDATE ChefAvailability SET end_time = %s WHERE availability_id = %s", (end_time, availability_id))
    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Chef availability updated successfully!"}

@router.delete("/availability/{availability_id}")
def delete_chef_availability(availability_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    DELETE FROM ChefAvailability
    WHERE availability_id = %s
    """

    cursor.execute(sql, (availability_id,))
    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Chef availability deleted successfully!"}

