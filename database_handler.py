import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs.db')

def init_db():
    """Initialize the database and create the logs table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            print_count INTEGER NOT NULL,
            ip_address TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_usage(session_id, print_count, ip_address=None):
    """Log a usage event to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usage_logs (session_id, timestamp, print_count, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (session_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), print_count, ip_address))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error logging to database: {e}")
        return False

def get_all_logs():
    """Retrieve all usage logs from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row # Return results as dictionaries
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usage_logs ORDER BY timestamp DESC')
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs
    except Exception as e:
        print(f"Error reading from database: {e}")
        return []

# Initialize the DB when this module is imported
init_db()
