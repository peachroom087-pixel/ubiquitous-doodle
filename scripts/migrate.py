#!/usr/bin/env python3
import sqlite3

def migrate():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            is_admin INTEGER NOT NULL,
            language TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Create logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            create_dttm TEXT NOT NULL,
            type TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    
    # Create schema_version table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY
        )
    ''')
    
    # Insert schema version 0 for Phase 0
    cursor.execute('DELETE FROM schema_version')
    cursor.execute('INSERT INTO schema_version (version) VALUES (0)')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()