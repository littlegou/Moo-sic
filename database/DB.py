import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASS")
DB_DATABASE = os.getenv("DB_DATABASE")
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE 
        )
        if connection.is_connected():
            print("Connection successful")
            return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
