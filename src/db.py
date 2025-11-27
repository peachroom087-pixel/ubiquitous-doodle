import sqlite3
from contextlib import contextmanager
import os
from typing import Optional


class DatabaseManager:
    def __init__(self, db_path: str = "events.db"):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Check if database file exists, raise error if not."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file {self.db_path} not found")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def execute(self, query: str, params: tuple = ()):
        """Execute a query that doesn't return results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def fetch(self, query: str, params: tuple = ()):
        """Execute a query that returns results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query: str, params: tuple = ()):
        """Execute a query that returns a single result."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()