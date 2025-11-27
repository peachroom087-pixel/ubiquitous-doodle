#!/usr/bin/env python3
import sqlite3
from datetime import datetime

def seed():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    
    # Insert seed data for Phase 0
    users_data = [
        ('admin', 1, 'ru', datetime.now().isoformat()),
        ('organizer1', 1, 'en', datetime.now().isoformat()),
        ('user1', 0, 'ru', datetime.now().isoformat()),
        ('user2', 0, 'en', datetime.now().isoformat())
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO users (login, is_admin, language, created_at)
        VALUES (?, ?, ?, ?)
    ''', users_data)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed()