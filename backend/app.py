from os import name

from fastapi import FastAPI
import mysql.connector

app = FastAPI()

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3307,
        user="ccuser",
        password="cc123!",
        database="chefconnection_db"
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

@app.get("/users")
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM User")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"users": users}


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


@app.get("/chefs")
def get_chefs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    chef_sql = """
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

    ORDER BY ranking_score DESC;
    """
    cursor.execute(chef_sql)
    chefs = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"chefs": chefs}

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
    AND status IN ('pending', 'confirmed')
    """
    cursor.execute(check_sql, (chef_id, booking_date, booking_time))
    existing = cursor.fetchone()

    if existing:
        cursor.close()
        conn.close()

        return {"message": "This time slot is already booked."}
    
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
    benefits: str = None
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    INSERT INTO MembershipPlan 
    (plan_name, price, benefits)
    VALUES (%s, %s, %s)
    """

    cursor.execute(sql, (plan_name, price, benefits))
    conn.commit()

    plan_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return {"message": "Membership plan created successfully!", "plan_id": plan_id}

@app.post("/chefs/{chef_id}/membership")
def add_chef_membership(
    chef_id: int,
    plan_id: int,
    memmbership_type: str = None,
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


