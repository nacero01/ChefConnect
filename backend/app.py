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
    c.chef_id, u.username, u.email
    FROM Chef c
    JOIN User u ON c.user_id = u.user_id
    ORDER BY c.rating DESC
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

