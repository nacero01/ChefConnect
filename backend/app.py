import os
import mysql.connector
from fastapi import FastAPI

app = FastAPI()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_hOST","127.0.0.1"),
        port=int(os.getenv("DB_PORT","3307")),
        user=os.getenv("DB_USER", "ccuser"),
        password=os.getenv("DB_PASSWORD","cc123!"),
        database=os.getenv("DB_NAME","chefconnection_db")
    )

@app.get("/")
def home():
    return {"message": "Welcome to Chef Connection!"}

@app.get("/roles")
def get_roles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Role")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"roles": roles}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    user_sql ="""
    SELECT
        u.user_id,
        u.username, 
        u.email, 
        r.role_name
    FROM User u
    JOIN Role r ON u.role_id = r.role_id
    WHERE u.user_id = %s
    """
    cursor.execute(user_sql, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        return {"message": "User not found"}
    return {"user": user}

@app.get("/chefs/{chef_id}")
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

@app.get("/bookings")
def get_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Booking")
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"bookings": bookings}

@app.post("/register")
def register_user(username: str, email: str, password_hash: str, role: str):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Determine role_id based on role name
    if role.lower().strip() == "chef":
        role_id = 2
    else:
        role_id = 3
    
    user_sql = """
    INSERT INTO User (username, email, password_hash, role_id)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(user_sql, (username, email, password_hash, role_id))
    conn.commit()

    user_id = cursor.lastrowid


    if role.lower().strip() == "chef":
        chef_sql = """
        INSERT INTO Chef (user_id)
        VALUES (%s)
        """
        cursor.execute(chef_sql, (user_id,))
        conn.commit()

    cursor.close()
    conn.close()
    return {"message": "User registered successfully!", "user_id": user_id, "role_id": role_id}


@app.post("/login")
def login(username: str, password: str):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    login_sql = """
    SELECT 
    u.user_id, u.username, u.email, r.role_name
    FROM User u
    JOIN Role r ON u.role_id = r.role_id
    WHERE u.username = %s AND u.password_hash = %s
    """

    cursor.execute(login_sql, (username, password))

    user = cursor.fetchone()

    cursor.close()
    conn.close() 

    if not user:
        return {"message": "Invalid username or password"}
    else:
        return {"message": "Login successful!", "user": user}

@app.put("/chefs/{chef_id}/profile")
def update_chef_profile(
    chef_id: int, 
    bio: str = None, 
    specialty: str = None
    ):
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

@app.post("/chefs/{chef_id}/availability")
def add_chef_availability(
    chef_id: int,
    day_of_week: str,
    start_time: str,
    end_time: str
):
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

@app.post("/bookings")
def create_booking(
    chef_id: int,
    user_id: int,
    booking_date: str,
    booking_time: str,
    customer_requests: str = None
):
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

@app.put("/bookings/{booking_id}/status")
def update_booking_status(booking_id: int, status: str):
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

@app.get("/users/{user_id}/bookings")
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

@app.get("/chefs/{chef_id}/bookings")
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

@app.post("/reviews")
def create_review(
    chef_id: int,
    user_id: int,
    rating: int,
    comment: str = None
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    review_sql = """
    INSERT INTO Review 
    (chef_id, user_id, rating, comment)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(review_sql, (chef_id, user_id, rating, comment))

    update_sql = """
    UPDATE Chef
    SET rating = (
        SELECT AVG(rating) 
        FROM Review 
        WHERE chef_id = %s
    )
    WHERE chef_id = %s
    """
    cursor.execute(update_sql, (chef_id, chef_id))
    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Review submitted successfully!"}

@app.get("/chefs/{chef_id}/reviews")
def get_chef_reviews(chef_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT 
        r.review_id, 
        r.rating, 
        r.comment, 
        r.created_at,
        u.username AS reviewer_name
    FROM Review r
    JOIN User u ON r.user_id = u.user_id
    WHERE r.chef_id = %s
    ORDER BY r.created_at DESC
    """

    cursor.execute(sql, (chef_id,))
    reviews = cursor.fetchall()

    cursor.close()
    conn.close()
    return {"reviews": reviews}

@app.post("/chefs/{chef_id}/dishes")
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

@app.get("/chefs/{chef_id}/dishes")
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

@app.post("/membership-plans")
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

@app.post("/chefs/{chef_id}/membership")
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

    cursor.execute(sql, (chef_id, plan_id, memmbership_type, start_date, end_date))
    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Chef membership added successfully!"}

@app.get("/chefs/search")
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

@app.post("/users/{user_id}/pantry")
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


@app.get("/users/{user_id}/pantry")
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

@app.post("/bookings/{booking_id}/ingredients")
def add_booking_ingredient(
    booking_id: int,
    ingredient_name: str,
    quantity: str = None,
    notes: str = None
):
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

@app.get("/bookings/{booking_id}/ingredients")
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

@app.put("/bookings/{booking_id}/cancel")
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

@app.put("/dishes/{dish_id}")
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

@app.delete("/dishes/{dish_id}")
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

@app.put("/availability/{availability_id}")
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

@app.delete("/availability/{availability_id}")
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

@app.post("/users/{user_id}/favorites/{chef_id}")
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

@app.get("/users/{user_id}/favorites")
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

@app.delete("/users/{user_id}/favorites/{chef_id}")
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

@app.get("/chefs/{chef_id}/booking-requests")
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