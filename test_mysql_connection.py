<<<<<<< HEAD
import mysql.connector
from mysql.connector import errorcode

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Hesogamol_01",  # Use your actual password here
        database="clients"
    )
    print("Successfully connected to MySQL and 'clients' database!")
    conn.close()
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database 'clients' does not exist")
    else:
=======
import mysql.connector
from mysql.connector import errorcode

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Hesogamol_01",  # Use your actual password here
        database="clients"
    )
    print("Successfully connected to MySQL and 'clients' database!")
    conn.close()
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database 'clients' does not exist")
    else:
>>>>>>> 684b464c7 (Initial commit)
        print(f"Error: {err}")