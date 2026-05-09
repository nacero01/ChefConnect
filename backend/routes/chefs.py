from fastapi import APIRouter
from database import get_db_connection
from schemas.chefs import ChefProfileRequest, AvailabilityRequest

router = APIRouter(tags=["Chefs"])

@router.get("/chefs/{chef_id}")
def get_chef(chef_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    chef_sql = """
    SELECT
        c.chef_id,
        u.username,
        u.email,
        c.bio,
        c.specialty,
        c.rating,
        CASE
            WHEN cm.end_date >= CURDATE() THEN 1
            ELSE 0
        END AS has_membership

        m.plan_name,
        cm.membership_type,
        cm.start_date,
        cm.end_date
    FROM Chef c
    JOIN User u ON c.user_id = u.user_id
    LEFT JOIN ChefMembership cm ON c.chef_id = cm.chef_id
    LEFT JOIN MembershipPlan m ON cm.plan_id = m.plan_id
    WHERE c.chef_id = %s
    """
    cursor.execute(chef_sql, (chef_id,))
    chef = cursor.fetchone()
    cursor.close()
    conn.close()
    if not chef:
        return {"message": "Chef not found"}
    return {"chef": chef}

@router.put("/chefs/{chef_id}/profile")
def update_chef_profile(chef_id: int, data:ChefProfileRequest):

    bio = data.bio 
    specialty = data.specialty

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    UPDATE Chef 
    SET bio = %s,
        specialty = %s 
    WHERE chef_id = %s
    """

    if bio is not None:
        cursor.execute("UPDATE Chef SET bio = %s WHERE chef_id = %s", (bio, chef_id))

    if specialty is not None:
        cursor.execute("UPDATE Chef SET specialty = %s WHERE chef_id = %s", (specialty, chef_id))

    cursor.execute(sql, (bio, specialty, chef_id))
    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Chef profile updated successfully!"} 

@router.post("/chefs/{chef_id}/availability")
def add_chef_availability(chef_id: int, data:AvailabilityRequest):

    day_of_week = data.day_of_week
    start_time = data.start_time
    end_time = data.end_time

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    check_sql = """
    SELECT *
    FROM ChefAvailability
    WHERE chef_id = %s 
    AND day_of_week = %s 
    AND ((start_time <= %s AND end_time > %s) 
    OR (start_time < %s AND end_time >= %s) 
    OR (start_time >= %s AND end_time <= %s))
    """
    cursor.execute(check_sql, (chef_id, day_of_week, start_time, start_time, end_time, end_time, start_time, end_time))
    existing = cursor.fetchone()
    if existing:
        cursor.close()
        conn.close()
        return {"message": "This time slot overlaps with existing availability."}
    
    insert_sql = """
    INSERT INTO ChefAvailability 
    (chef_id, day_of_week, start_time, end_time)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(insert_sql,(chef_id, day_of_week, start_time, end_time))
    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Chef availability added successfully!"} 

@router.get("/chefs/{chef_id}/bookings")
def get_chef_bookings(chef_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT 
        b.booking_id, 
        b.booking_date, 
        b.booking_time, 
        b.status, 
        b.customer_requests,
        u.user_id AS customer_id,
        u.username AS customer_name
    FROM Booking b
    JOIN User u ON b.user_id = u.user_id
    WHERE b.chef_id = %s
    ORDER BY b.booking_date DESC, b.booking_time DESC
    """

    cursor.execute(sql, (chef_id,))
    bookings = cursor.fetchall()

    cursor.close()
    conn.close()
    return {"bookings": bookings}

@router.get("/chefs/{chef_id}/booking-requests")
def get_chef_booking_requests(chef_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    bookingReq_sql = """
    SELECT
        b.booking_id,
        b.booking_date,
        b.booking_time,
        b.status,
        b.customer_requests,
        u.user_id AS client_id,
        u.username AS client_username,
        u.email AS client_email
    FROM Booking b
    JOIN User u ON b.user_id = u.user_id
    WHERE b.chef_id = %s
    AND b.status = 'pending'
    ORDER BY b.booking_date, b.booking_time
    """

    cursor.execute(bookingReq_sql, (chef_id,))
    requests = cursor.fetchall()

    cursor.close()
    conn.close()

    return {"booking_requests": requests}

@router.get("/chefs/search")
def search_chefs(
    specialty: str = None,
    min_rating: float = None,
    day_of_week: str = None
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT
        Chef.chef_id,
        User.username,
        Chef.bio,
        Chef.specialty,
        Chef.rating,
        CASE
            WHEN ChefMembership.end_date >= CURDATE() THEN 1
            ELSE 0
        END AS has_membership,

        (
            Chef.rating +
            CASE
                WHEN ChefMembership.end_date >= CURDATE() THEN 0.5
                ELSE 0
            END
        ) AS ranking_score
    FROM Chef
    JOIN User ON Chef.user_id = User.user_id
    LEFT JOIN ChefMembership ON Chef.chef_id = ChefMembership.chef_id
    LEFT JOIN ChefAvailability ON ChefAvailability.chef_id = Chef.chef_id
    WHERE 1=1
    """

    params = []

    if specialty:
        sql += " AND Chef.specialty LIKE %s"
        params.append(f"%{specialty}%")

    if min_rating:
        sql += " AND Chef.rating >= %s"
        params.append(min_rating)

    if day_of_week:
        sql += "AND ChefAvailability.day_of_week = %s"
        params.append(day_of_week)

    sql += " ORDER BY ranking_score DESC"
    cursor.execute(sql, tuple(params))
    chefs = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"chefs": chefs}