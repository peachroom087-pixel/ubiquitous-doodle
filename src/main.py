#!/usr/bin/env python3
import sys
import os
import atexit
from datetime import datetime

# Add src directory to Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import DatabaseManager
from services.auth import AuthService
from i18n.loader import LocaleLoader
from i18n.translator import Translator


class EventManagerApp:
    def __init__(self):
        # Check for lock file to prevent multiple instances
        if os.path.exists('.lock'):
            print("Application is already running (lock file exists)", file=sys.stderr)
            sys.exit(1)
        
        # Create lock file
        with open('.lock', 'w') as f:
            f.write(str(os.getpid()))
        
        # Register cleanup function to remove lock file on normal exit
        atexit.register(self.cleanup)
        
        import os
        self.is_test_mode = 'TEST_MODE' in os.environ
        self.session_replay_file = "session_replay_test.txt" if self.is_test_mode else "session_replay.txt"
        self.start_time = datetime.now()
        
        try:
            self.db = DatabaseManager()
        except FileNotFoundError:
            self.log_to_file("CRITICAL", "DB_NOT_FOUND", "Database file events.db not found")
            print("ERROR: Database file events.db not found", file=sys.stderr)
            sys.exit(1001)  # DB_NOT_FOUND error code
        
        self.auth_service = AuthService(self.db)
        self.locale_loader = LocaleLoader()
        self.translator = Translator(self.locale_loader)
        
        # Initialize user info
        self.current_user = None
        self.user_id = None

    def cleanup(self):
        """Remove lock file on exit."""
        if os.path.exists('.lock'):
            os.remove('.lock')

    def log_to_file(self, level: str, event_type: str, message: str):
        """Log to session replay file."""
        if self.is_test_mode:
            # Use fixed timestamp for tests to ensure consistency
            timestamp = "2024-01-01T00:00:00"
        else:
            timestamp = datetime.now().isoformat()
        with open(self.session_replay_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {level} - {event_type}: {message}\n")

    def log_to_db(self, user_id: int, message: str):
        """Log to database."""
        self.db.execute(
            "INSERT INTO logs (create_dttm, type, user_id, message) VALUES (?, 'user_action', ?, ?)",
            (datetime.utcnow().isoformat(), user_id, message)
        )

    def get_user_input(self, prompt_key: str, **kwargs) -> str:
        """Get user input and log it to session replay."""
        prompt = self.translator._(prompt_key, **kwargs)
        print(prompt, end='', flush=True)
        
        # Log to session replay
        self.log_to_file("INPUT", "prompt", prompt)
        
        user_input = input()
        self.log_to_file("INPUT", "user_input", user_input)
        
        return user_input

    def show_message(self, message_key: str, **kwargs):
        """Show a message to the user and log it."""
        message = self.translator._(message_key, **kwargs)
        print(message)
        self.log_to_file("OUTPUT", "message", message)

    def authenticate_user(self):
        """Handle user authentication."""
        while True:
            login = self.get_user_input("auth.login_prompt").strip()
            
            if not self.auth_service.validate_login(login):
                self.show_message("error.invalid_login")
                self.log_to_db(0, f"Invalid login attempt: {login}")
                continue
            
            user = self.auth_service.get_user(login)
            if user:
                # Existing user
                user_id, login, is_admin, language, created_at = user
                self.user_id = user_id
                self.current_user = {'id': user_id, 'login': login, 'is_admin': is_admin}
                self.translator.set_language(language)
                
                self.log_to_db(user_id, f"User {login} logged in")
                self.log_to_file("INFO", "login", f"User {login} logged in as {'admin' if is_admin else 'regular user'}")
                break
            else:
                # New user - ask for language preference
                while True:
                    lang_choice = self.get_user_input("auth.language_prompt").strip().lower()
                    if lang_choice in ['ru', 'en']:
                        language = lang_choice
                        break
                    else:
                        self.show_message("error.invalid_language")
                
                # Create new user
                user_id = self.auth_service.create_user(login, language)
                self.user_id = user_id
                self.current_user = {'id': user_id, 'login': login, 'is_admin': 0}
                self.translator.set_language(language)
                
                self.log_to_db(user_id, f"New user {login} created with language {language}")
                self.log_to_file("INFO", "create_user", f"New user {login} created with language {language}")
                break

    def show_main_menu(self):
        """Show the main menu."""
        while True:
            self.show_message("main_menu.welcome", username=self.current_user['login'])
            self.show_message("main_menu.exit")
            
            choice = self.get_user_input("main_menu.choice_prompt").strip()
            
            if choice == '0':
                self.log_to_db(self.user_id, "User chose to exit")
                self.log_to_file("INFO", "exit", "User chose to exit")
                return
            else:
                self.show_message("error.invalid_menu_choice")
                self.log_to_db(self.user_id, f"Invalid menu choice: {choice}")
                self.log_to_file("WARNING", "invalid_menu", f"Invalid menu choice: {choice}")

    def run(self):
        """Main application run method."""
        self.authenticate_user()
        self.show_main_menu()


def main():
    app = EventManagerApp()
    app.run()


if __name__ == "__main__":
    main()