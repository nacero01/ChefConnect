from fastapi import APIRouter
from database import get_db_connection
from schemas.bookings import BookingRequest, BookingStatusRequest, BookingIngredientRequest

router = APIRouter(tags=["Bookings"])

@router.get("/bookings")
def get_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Booking")
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"bookings": bookings}

@router.post("/bookings")
def create_booking(data:BookingRequest):
    chef_id = data.chef_id
    user_id = data.user_id
    booking_date = data.booking_date
    booking_time = data.booking_time
    customer_requests = data.customer_requests

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    check_sql = """
    SELECT *
    FROM Booking
    WHERE chef_id = %s 
    AND booking_date = %s 
    AND booking_time = %s
    AND status IN ('pending', 'accepted')
    """
    cursor.execute(check_sql, (chef_id, booking_date, booking_time))
    existing = cursor.fetchone()

    if existing:
        cursor.close()
        conn.close()

        return {"message": "This time slot is already booked."}
    
    availability_sql = """
    SELECT *
    FROM ChefAvailability
    WHERE chef_id = %s
    AND day_of_week = DAYNAME(%s)
    AND %s BETWEEN start_time AND end_time
    """

    cursor.execute(
        availability_sql,
        (chef_id, booking_date, booking_time)
    )

    availability = cursor.fetchone()

    if not availability:
        cursor.close()
        conn.close()

        return {
            "error": "Chef is not available at this time"
        }
        
    booking_sql = """
    INSERT INTO Booking 
    (
    chef_id, 
    user_id, 
    booking_date, 
    booking_time,
    status,
    customer_requests
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(booking_sql,(chef_id, user_id, booking_date, booking_time, "pending", customer_requests))
    conn.commit()

    booking_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return {"message": "Booking created successfully!", "booking_id": booking_id, "status": "pending"}

@router.put("/bookings/{booking_id}/status")
def update_booking_status(booking_id: int, data:BookingStatusRequest):

    status = data.status

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    allowed_statuses = ["pending", "accepted", "declined", "cancelled", "completed"]

    if status not in allowed_statuses:
        cursor.close()
        conn.close()
        return {"message": "Invalid status. Please choose from: pending, accepted, declined, cancelled, completed"}

    sql = """
    UPDATE Booking 
    SET status = %s
    WHERE booking_id = %s
    """

    cursor.execute(sql, (status, booking_id))
    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Booking status updated successfully!",
            "booking_id": booking_id,
            "new_status": status
            }

@router.get("/users/{user_id}/bookings")
def get_user_bookings(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT 
        b.booking_id, 
        b.booking_date, 
        b.booking_time, 
        b.status, 
        b.customer_requests,
        c.chef_id,
        u.username AS chef_name
    FROM Booking b
    JOIN Chef c ON b.chef_id = c.chef_id
    JOIN User u ON c.user_id = u.user_id
    WHERE b.user_id = %s
    ORDER BY b.booking_date DESC, b.booking_time DESC
    """

    cursor.execute(sql, (user_id,))
    bookings = cursor.fetchall()

    cursor.close()
    conn.close()
    return {"bookings": bookings}

@router.put("/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    UPDATE Booking 
    SET status = 'cancelled'
    WHERE booking_id = %s
    """

    cursor.execute(sql, (booking_id,))
    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Booking cancelled successfully!", "booking_id": booking_id}


@router.post("/bookings/{booking_id}/ingredients")
def add_booking_ingredient(booking_id: int, data:BookingIngredientRequest):

    ingredient_name = data.ingredient_name
    quantity = data.quantity
    notes = data.notes

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    INSERT INTO BookingIngredientRequest 
    (booking_id, ingredient_name, quantity, notes)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(sql, (booking_id, ingredient_name, quantity, notes))
    conn.commit()

    ingredient_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return {"message": "Ingredient added to booking successfully!", "ingredient_id": ingredient_id}

@router.get("/bookings/{booking_id}/ingredients")
def get_booking_ingredients(booking_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT *
    FROM BookingIngredientRequest
    WHERE booking_id = %s
    """

    cursor.execute(sql, (booking_id,))
    ingredients = cursor.fetchall()

    cursor.close()
    conn.close()
    return {"ingredients": ingredients}