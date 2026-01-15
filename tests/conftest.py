"""
Shared pytest fixtures and configuration for HabitForge tests.

This module provides reusable test fixtures for database setup,
sample data, and common testing utilities.
"""

import sys
import sqlite3
from pathlib import Path
from datetime import date, timedelta
from typing import Optional
import pytest

# Add app directory to path for imports
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

# Mock Kivy logger before importing app modules
class MockLogger:
    """Mock Kivy logger for testing without Kivy runtime."""

    @staticmethod
    def info(msg):
        pass

    @staticmethod
    def warning(msg):
        pass

    @staticmethod
    def error(msg):
        pass

    @staticmethod
    def debug(msg):
        pass


# Mock kivy.logger module
sys.modules['kivy.logger'] = type('MockKivyLogger', (), {'Logger': MockLogger})()


# Test Database Fixtures

@pytest.fixture(scope="function")
def test_db():
    """
    Provides an in-memory SQLite database for testing.

    The database is created fresh for each test and automatically
    cleaned up after the test completes.

    Yields:
        sqlite3.Connection: In-memory database connection
    """
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    # Create tables
    cursor = conn.cursor()

    # Habits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            goal_type TEXT NOT NULL CHECK(goal_type IN ('daily', 'weekly', 'monthly')),
            goal_count INTEGER NOT NULL CHECK(goal_count > 0 AND goal_count <= 100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            archived INTEGER DEFAULT 0,
            UNIQUE(name COLLATE NOCASE)
        )
    """)

    # Completions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            date DATE NOT NULL,
            count INTEGER NOT NULL DEFAULT 1,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
            UNIQUE(habit_id, date)
        )
    """)

    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_completions_habit_date
        ON completions(habit_id, date)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_habits_archived
        ON habits(archived)
    """)

    # Create settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    yield conn

    # Cleanup
    conn.close()


@pytest.fixture
def sample_habit_data():
    """
    Provides a valid habit data dictionary for testing.

    Returns:
        dict: Valid habit creation data
    """
    return {
        'name': 'Morning Exercise',
        'color': '#E57373',
        'goal_type': 'daily',
        'goal_count': 1
    }


@pytest.fixture
def sample_habits_data():
    """
    Provides multiple valid habit data dictionaries for testing.

    Returns:
        list[dict]: List of valid habit creation data
    """
    return [
        {
            'name': 'Morning Exercise',
            'color': '#E57373',
            'goal_type': 'daily',
            'goal_count': 1
        },
        {
            'name': 'Read Book',
            'color': '#64B5F6',
            'goal_type': 'daily',
            'goal_count': 30  # 30 minutes
        },
        {
            'name': 'Gym',
            'color': '#81C784',
            'goal_type': 'weekly',
            'goal_count': 3
        },
        {
            'name': 'Meditation',
            'color': '#BA68C8',
            'goal_type': 'monthly',
            'goal_count': 20
        }
    ]


@pytest.fixture
def create_test_habit(test_db):
    """
    Factory fixture to create test habits in the database.

    Usage:
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)

    Args:
        test_db: Test database fixture

    Returns:
        function: Function to create a habit and return its ID
    """
    def _create_habit(
        name: str = 'Test Habit',
        color: str = '#E57373',
        goal_type: str = 'daily',
        goal_count: int = 1,
        archived: int = 0
    ) -> int:
        cursor = test_db.cursor()
        cursor.execute(
            """
            INSERT INTO habits (name, color, goal_type, goal_count, archived)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, color, goal_type, goal_count, archived)
        )
        test_db.commit()
        return cursor.lastrowid

    return _create_habit


@pytest.fixture
def create_test_completion(test_db):
    """
    Factory fixture to create test completions in the database.

    Usage:
        completion_id = create_test_completion(habit_id, date(2024, 12, 15), 5)

    Args:
        test_db: Test database fixture

    Returns:
        function: Function to create a completion and return its ID
    """
    def _create_completion(
        habit_id: int,
        completion_date: date,
        count: int = 1
    ) -> int:
        cursor = test_db.cursor()
        cursor.execute(
            """
            INSERT INTO completions (habit_id, date, count)
            VALUES (?, ?, ?)
            """,
            (habit_id, completion_date.isoformat(), count)
        )
        test_db.commit()
        return cursor.lastrowid

    return _create_completion


# Date Testing Fixtures

@pytest.fixture
def mock_today():
    """
    Provides a function to mock the current date for testing.

    Returns a function that can be used with monkeypatch to override
    date_utils.get_today() for controlled date testing.
    """
    def _mock_today(mock_date: date):
        """Returns a function that returns the mocked date."""
        return lambda: mock_date

    return _mock_today


# Test Data Generators

def generate_date_range(start_date: date, end_date: date):
    """
    Generate a list of dates between start and end (inclusive).

    Args:
        start_date: First date in range
        end_date: Last date in range

    Returns:
        list[date]: List of dates in range
    """
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def get_test_date(days_ago: int = 0) -> date:
    """
    Get a test date relative to today.

    Args:
        days_ago: Number of days in the past (positive) or future (negative)

    Returns:
        date: Test date
    """
    return date.today() - timedelta(days=days_ago)
