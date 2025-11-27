import re
from datetime import datetime
from typing import Optional, Tuple
import sys
import os

# Add src directory to Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db import DatabaseManager


class AuthService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def validate_login(self, login: str) -> bool:
        """Validate login format: 3-20 chars, a-z, 0-9, _"""
        if len(login) < 3 or len(login) > 20:
            return False
        return bool(re.match(r'^[a-z0-9_]+$', login))

    def get_user(self, login: str) -> Optional[Tuple[int, str, int, str, str]]:
        """Get user by login."""
        result = self.db.fetch_one(
            "SELECT id, login, is_admin, language, created_at FROM users WHERE login = ?",
            (login,)
        )
        return result

    def create_user(self, login: str, language: str) -> int:
        """Create new user with specified language."""
        user_id = self.db.execute(
            "INSERT INTO users (login, is_admin, language, created_at) VALUES (?, 0, ?, ?)",
            (login, language, datetime.now().isoformat())
        )
        return user_id

    def update_user_language(self, user_id: int, language: str):
        """Update user's language preference."""
        self.db.execute(
            "UPDATE users SET language = ? WHERE id = ?",
            (language, user_id)
        )