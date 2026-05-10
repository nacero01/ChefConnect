import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST","mysql"),
        port=int(os.getenv("DB_PORT","3306")),
        user=os.getenv("DB_USER", "ccuser"),
        password=os.getenv("DB_PASSWORD","cc123!"),
        database=os.getenv("DB_NAME","chefconnection_db")
    )
