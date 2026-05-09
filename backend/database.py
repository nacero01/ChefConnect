import os
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_hOST","127.0.0.1"),
        port=int(os.getenv("DB_PORT","3307")),
        user=os.getenv("DB_USER", "ccuser"),
        password=os.getenv("DB_PASSWORD","cc123!"),
        database=os.getenv("DB_NAME","chefconnection_db")
    )
