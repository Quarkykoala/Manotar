import sqlite3
import os
from datetime import datetime

DATABASE = '/tmp/users.db'

def init_db():
    # Ensure the /tmp directory exists (usually it does, but it's good to check)
    if not os.path.exists('/tmp'):
        os.makedirs('/tmp')
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            phone_number TEXT PRIMARY KEY,
            access_code TEXT,
            conversation_started INTEGER DEFAULT 0,
            last_message_time TEXT,
            message_count INTEGER DEFAULT 0
        )
    ''')
    # Create conversation_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT,
            FOREIGN KEY(phone_number) REFERENCES users(phone_number)
        )
    ''')
    conn.commit()
    conn.close()

    # Set permissions (be cautious with this in production)
    try:
        os.chmod(DATABASE, 0o666)
    except Exception as e:
        print(f"Warning: Could not set permissions for {DATABASE}: {e}")

def get_user(phone_number):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'phone_number': row[0],
            'access_code': row[1],
            'conversation_started': bool(row[2]),
            'last_message_time': row[3],
            'message_count': row[4]
        }
    return None

def create_user(phone_number, access_code):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (phone_number, access_code) VALUES (?, ?)
    ''', (phone_number, access_code))
    conn.commit()
    conn.close()

def update_user(phone_number, key, value):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f'''
        UPDATE users SET {key} = ? WHERE phone_number = ?
    ''', (value, phone_number))
    conn.commit()
    conn.close()

def add_conversation(phone_number, role, content):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    cursor.execute('''
        INSERT INTO conversation_history (phone_number, role, content, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (phone_number, role, content, timestamp))
    conn.commit()
    conn.close()

def get_conversation_history(phone_number):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content FROM conversation_history
        WHERE phone_number = ?
        ORDER BY timestamp ASC
    ''', (phone_number,))
    rows = cursor.fetchall()
    conn.close()
    return [{'role': row[0], 'content': row[1]} for row in rows]