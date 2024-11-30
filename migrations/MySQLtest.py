import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    # Get connection details from environment variables
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_name = os.getenv("DB_NAME")
    db_socket = os.getenv("DB_SOCKET")
    db_host = os.getenv("DB_HOST", "localhost")

    # Determine connection method based on environment
    if db_socket and os.name != 'nt':  # Unix-like systems
        conn = pymysql.connect(
            unix_socket=db_socket,
            user=db_user,
            password=db_pass,
            db=db_name
        )
    else:  # Windows or when DB_SOCKET is not set
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            db=db_name
        )

    print("Successfully connected to MySQL!")
    
    # Test the connection by executing a simple query
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"Database version: {version[0]}")

    conn.close()

except pymysql.MySQLError as err:
    print(f"Error: {err}")