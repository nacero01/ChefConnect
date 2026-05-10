from fastapi import APIRouter
from database import get_db_connection
from schemas.users import RegisterRequest, LoginRequest
from utils import success_response, error_response

router = APIRouter(tags=["Users"])

@router.get("/roles")
def get_roles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Role")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()
    return success_response("Roles retrieved successfully",roles)

@router.get("/users/{user_id}")
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
        return error_response("User not found")
    return success_response("User retrieved successfully",user)

@router.post("/register")
def register_user(data: RegisterRequest):

    username = data.username
    email = data.email
    password_hash = data.password
    role = data.role

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

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
    return success_response("User registered successfully!", user_id, role_id)

@router.post("/login")
def login(data:LoginRequest):

    username = data.username
    password = data.password

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
        return error_response("Invalid username or password")
    else:
        return success_response("Login successful!", user)

