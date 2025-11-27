import subprocess
import pytest
import json
import os
import sqlite3
from pathlib import Path


@pytest.fixture(scope="function", autouse=True)
def setup_phase_0():
    """Setup Phase 0 before running tests."""
    subprocess.run(["make", "setup-phase-0"], check=True, cwd="/workspace")
    yield
    # Cleanup can be done here if needed


def run_app_with_input(input_lines):
    """Helper to run the app with provided input lines."""
    env = os.environ.copy()
    env['TEST_MODE'] = '1'  # Set test mode to use session_replay_test.txt
    
    proc = subprocess.Popen(
        ["python", "src/main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/workspace",
        env=env
    )
    
    stdout, stderr = proc.communicate(input="\n".join(input_lines))
    return stdout, stderr, proc.returncode


def load_locale(lang):
    """Load locale file for testing."""
    locale_path = f"/workspace/data/locales/{lang}.json"
    with open(locale_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_error_locale():
    """Load error locale file for testing."""
    locale_path = "/workspace/data/locales/errors.json"
    with open(locale_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_db_not_found():
    """Test scenario: запуск без БД → error.db_not_found, выход"""
    # Remove the database file
    if os.path.exists("/workspace/events.db"):
        os.remove("/workspace/events.db")
    
    proc = subprocess.Popen(
        ["python", "src/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/workspace"
    )
    
    stdout, stderr = proc.communicate()
    
    # Should exit with code 1001 (DB_NOT_FOUND)
    assert proc.returncode == 1001
    
    # Error message should appear in stderr
    error_locale = load_error_locale()
    expected_error = error_locale["error.db_not_found"]
    assert "Database file events.db not found" in stderr


def test_existing_user_ru():
    """Test scenario: вход существующим user1 → welcome на русском, меню, выход"""
    ru_locale = load_locale("ru")
    
    input_lines = [
        "user1",  # Login
        "0"       # Exit from menu
    ]
    
    stdout, stderr, returncode = run_app_with_input(input_lines)
    
    # Should exit successfully
    assert returncode == 0
    
    # Check that Russian welcome message appears
    expected_welcome = ru_locale["main_menu.welcome"].format(username="user1")
    assert expected_welcome in stdout
    
    # Check that Russian exit option appears
    expected_exit = ru_locale["main_menu.exit"]
    assert expected_exit in stdout


def test_existing_user_en():
    """Test scenario: вход существующим user2 → welcome на английском, меню, выход"""
    en_locale = load_locale("en")
    
    input_lines = [
        "user2",  # Login
        "0"       # Exit from menu
    ]
    
    stdout, stderr, returncode = run_app_with_input(input_lines)
    
    # Should exit successfully
    assert returncode == 0
    
    # Check that English welcome message appears
    expected_welcome = en_locale["main_menu.welcome"].format(username="user2")
    assert expected_welcome in stdout
    
    # Check that English exit option appears
    expected_exit = en_locale["main_menu.exit"]
    assert expected_exit in stdout


def test_new_user_ru():
    """Test scenario: вход новым test_user_ru → выбор языка ru, welcome, меню, выход"""
    ru_locale = load_locale("ru")
    
    input_lines = [
        "test_user_ru",  # New login
        "ru",            # Language choice
        "0"              # Exit from menu
    ]
    
    stdout, stderr, returncode = run_app_with_input(input_lines)
    
    # Should exit successfully
    assert returncode == 0
    
    # Check that Russian welcome message appears
    expected_welcome = ru_locale["main_menu.welcome"].format(username="test_user_ru")
    assert expected_welcome in stdout
    
    # Check that Russian exit option appears
    expected_exit = ru_locale["main_menu.exit"]
    assert expected_exit in stdout
    
    # Verify user was created in database
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    result = cursor.execute("SELECT language FROM users WHERE login = ?", ("test_user_ru",)).fetchone()
    conn.close()
    
    assert result is not None
    assert result[0] == "ru"


def test_new_user_en():
    """Test scenario: вход новым test_user_en → выбор языка en, welcome, меню, выход"""
    en_locale = load_locale("en")
    
    input_lines = [
        "test_user_en",  # New login
        "en",            # Language choice
        "0"              # Exit from menu
    ]
    
    stdout, stderr, returncode = run_app_with_input(input_lines)
    
    # Should exit successfully
    assert returncode == 0
    
    # Check that English welcome message appears
    expected_welcome = en_locale["main_menu.welcome"].format(username="test_user_en")
    assert expected_welcome in stdout
    
    # Check that English exit option appears
    expected_exit = en_locale["main_menu.exit"]
    assert expected_exit in stdout
    
    # Verify user was created in database
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    result = cursor.execute("SELECT language FROM users WHERE login = ?", ("test_user_en",)).fetchone()
    conn.close()
    
    assert result is not None
    assert result[0] == "en"


def test_invalid_login():
    """Test scenario: невалидный логин → ошибка, повтор ввода"""
    error_locale = load_error_locale()
    ru_locale = load_locale("ru")
    
    input_lines = [
        "ab",      # Invalid login (too short)
        "user1",   # Valid login
        "0"        # Exit from menu
    ]
    
    stdout, stderr, returncode = run_app_with_input(input_lines)
    
    # Should exit successfully after correction
    assert returncode == 0
    
    # Check that invalid login error message appears
    expected_error = ru_locale["error.invalid_login"]
    assert expected_error in stdout
    
    # Check that login was eventually successful
    expected_welcome = ru_locale["main_menu.welcome"].format(username="user1")
    assert expected_error in stdout or expected_welcome in stdout


def test_invalid_menu_choice():
    """Test scenario: неверный пункт меню → ошибка, повтор меню"""
    ru_locale = load_locale("ru")
    
    input_lines = [
        "user1",   # Login
        "1",       # Invalid menu choice
        "0"        # Exit from menu
    ]
    
    stdout, stderr, returncode = run_app_with_input(input_lines)
    
    # Should exit successfully after correction
    assert returncode == 0
    
    # Check that invalid menu choice error message appears
    expected_error = ru_locale["error.invalid_menu_choice"]
    assert expected_error in stdout
    
    # Check that welcome message appears
    expected_welcome = ru_locale["main_menu.welcome"].format(username="user1")
    assert expected_welcome in stdout