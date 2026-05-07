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

@app.get("/chefs")
def get_chefs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Chef")
    chefs = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"chefs": chefs}

@app.get("/bookings")
def get_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Booking")
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"bookings": bookings}

@app.get("/dishes")
def get_dishes():    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Dish")
    dishes = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"dishes": dishes}

@app.post("/login")
def login(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM User WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return {"message": "Login successful", "user": user}
    else:
        return {"message": "Invalid username or password"}

@app.post("/register")
def register_user(username: str, email: str, password_hash: str, role: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if role == 'Chef':
        role_id = 2
    else:
        role_id = 3
    
    user_sql = """
    INSERT INTO User (username, email, password_hash, role_id)
    VALUES (%s, %s, %s, %s)
    """

    conn.commit()

    user_id = cursor.lastrowid

    cursor.execute(user_sql, (username, email, password_hash, role_id))
    if role == "chef":
        chef_sql = """
        INSERT INTO Chef (user_id)
        VALUES (%s)
        """
        cursor.execute(chef_sql, (user_id))
        conn

    cursor.close()
    conn.close()
    return {"message": "User registered successfully!"}
