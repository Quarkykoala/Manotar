"""
Run SQL Migrations for Manobal Platform

This script directly executes SQL statements to update the database
schema to match our model changes for API v1.
"""
import os
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the SQLite database
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'manobal.db')

def check_table_exists(conn, table_name):
    """Check if a table exists in the database"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    return cursor.fetchone() is not None

def check_column_exists(conn, table_name, column_name):
    """Check if a column exists in a table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    return any(column[1] == column_name for column in columns)

def run_migrations():
    """Run SQL migrations to update the database schema"""
    logger.info(f"Starting SQL migrations on {DB_PATH}")
    
    # Check if the database file exists
    if not os.path.exists(DB_PATH):
        logger.error(f"Database file not found: {DB_PATH}")
        return False
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        conn.execute("BEGIN TRANSACTION;")
        
        # Update User table
        if check_table_exists(conn, 'user'):
            logger.info("Updating User table")
            if not check_column_exists(conn, 'user', 'conversation_started'):
                cursor.execute("ALTER TABLE user ADD COLUMN conversation_started BOOLEAN;")
            if not check_column_exists(conn, 'user', 'created_at'):
                cursor.execute("ALTER TABLE user ADD COLUMN created_at TIMESTAMP;")
            if not check_column_exists(conn, 'user', 'updated_at'):
                cursor.execute("ALTER TABLE user ADD COLUMN updated_at TIMESTAMP;")
        
        # Update Message table
        if check_table_exists(conn, 'message'):
            logger.info("Updating Message table")
            if not check_column_exists(conn, 'message', 'is_from_user'):
                cursor.execute("ALTER TABLE message ADD COLUMN is_from_user BOOLEAN DEFAULT TRUE;")
            if not check_column_exists(conn, 'message', 'sentiment_score'):
                cursor.execute("ALTER TABLE message ADD COLUMN sentiment_score FLOAT;")
            if not check_column_exists(conn, 'message', 'department'):
                cursor.execute("ALTER TABLE message ADD COLUMN department VARCHAR(50);")
            if not check_column_exists(conn, 'message', 'location'):
                cursor.execute("ALTER TABLE message ADD COLUMN location VARCHAR(50);")
        
        # Update KeywordStat table
        if check_table_exists(conn, 'keyword_stat'):
            logger.info("Updating KeywordStat table")
            if not check_column_exists(conn, 'keyword_stat', 'department'):
                cursor.execute("ALTER TABLE keyword_stat ADD COLUMN department VARCHAR(50);")
            if not check_column_exists(conn, 'keyword_stat', 'location'):
                cursor.execute("ALTER TABLE keyword_stat ADD COLUMN location VARCHAR(50);")
        
        # Create SentimentLog table
        if not check_table_exists(conn, 'sentiment_log'):
            logger.info("Creating SentimentLog table")
            cursor.execute("""
            CREATE TABLE sentiment_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                department VARCHAR(50),
                location VARCHAR(50),
                sentiment_score FLOAT NOT NULL,
                message_id INTEGER,
                timestamp TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (message_id) REFERENCES message(id)
            );
            """)
        
        # Create AuthUser table
        if not check_table_exists(conn, 'auth_user'):
            logger.info("Creating AuthUser table")
            cursor.execute("""
            CREATE TABLE auth_user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(100) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                password_hash VARCHAR(200) NOT NULL,
                role VARCHAR(20) NOT NULL,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                last_login TIMESTAMP
            );
            """)
        
        # Create AuditLog table
        if not check_table_exists(conn, 'audit_log'):
            logger.info("Creating AuditLog table")
            cursor.execute("""
            CREATE TABLE audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action VARCHAR(100) NOT NULL,
                target VARCHAR(100),
                details TEXT,
                ip_address VARCHAR(50),
                timestamp TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES auth_user(id)
            );
            """)
        
        # Commit the transaction
        conn.execute("COMMIT;")
        logger.info("Database schema updated successfully")
        return True
    
    except Exception as e:
        # Roll back any changes if there was an error
        conn.execute("ROLLBACK;")
        logger.error(f"Error updating database schema: {str(e)}")
        return False
    
    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    if run_migrations():
        logger.info("SQL migration complete")
    else:
        logger.error("SQL migration failed") 