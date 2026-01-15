"""
Database Operations for HabitForge

This module handles all SQLite database operations for habits.
Uses context managers for safe connection handling.
"""

import sqlite3
import os
from typing import List, Dict, Optional
from pathlib import Path
from datetime import date
from .schemas import Habit, Completion
from kivy.logger import Logger


def get_db_path() -> str:
    """
    Get the database file path.

    Returns appropriate path based on environment:
    - Android: App's user_data_dir
    - Desktop: Current directory (for development)

    Returns:
        str: Absolute path to database file
    """
    try:
        from kivy.app import App

        app = App.get_running_app()
        if app and hasattr(app, "user_data_dir"):
            # Running on Android or in Kivy app
            db_dir = app.user_data_dir
            Path(db_dir).mkdir(parents=True, exist_ok=True)
            db_path = os.path.join(db_dir, "habitforge.db")
            Logger.info(f"Database: Using path {db_path}")
            return db_path
    except Exception as e:
        Logger.warning(f"Database: Could not get app user_data_dir: {e}")

    # Fallback to app/data directory for development
    db_dir = Path(__file__).parent.parent / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = str(db_dir / "habitforge.db")
    Logger.info(f"Database: Using development path {db_path}")
    return db_path


def get_connection() -> sqlite3.Connection:
    """
    Create a database connection.

    Returns:
        sqlite3.Connection: Database connection with Row factory enabled
    """
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def init_database() -> None:
    """
    Initialize the database by creating tables if they don't exist.

    Creates the habits table with all constraints.
    Safe to call multiple times (uses IF NOT EXISTS).
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Create habits table
            cursor.execute(
                """
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
                """
            )

            # Create index on archived column
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_habits_archived
                ON habits(archived)
                """
            )

            # Create completions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    count INTEGER NOT NULL DEFAULT 1,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
                    UNIQUE(habit_id, date)
                )
                """
            )

            # Create index on (habit_id, date) for query performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_completions_habit_date
                ON completions(habit_id, date)
                """
            )

            # Create settings table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Enable foreign key constraints (SQLite disables by default)
            cursor.execute("PRAGMA foreign_keys = ON")

            # Initialize default language setting if not exists
            cursor.execute(
                """
                INSERT OR IGNORE INTO settings (key, value)
                VALUES ('language', 'en')
                """
            )

            conn.commit()
            Logger.info("Database: Successfully initialized tables")
    except sqlite3.Error as e:
        Logger.error(f"Database: Failed to initialize: {e}")
        raise


def create_habit(name: str, color: str, goal_type: str, goal_count: int) -> int:
    """
    Create a new habit in the database.

    Args:
        name: Habit name (will be validated by Pydantic before calling this)
        color: Hex color code (#RRGGBB)
        goal_type: 'daily', 'weekly', or 'monthly'
        goal_count: Target count per period (1-100)

    Returns:
        int: ID of the newly created habit

    Raises:
        sqlite3.IntegrityError: If habit name already exists (UNIQUE constraint)
        sqlite3.Error: For other database errors
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO habits (name, color, goal_type, goal_count)
                VALUES (?, ?, ?, ?)
                """,
                (name, color, goal_type, goal_count),
            )
            conn.commit()
            habit_id = cursor.lastrowid
            Logger.info(f"Database: Created habit '{name}' with ID {habit_id}")
            return habit_id
    except sqlite3.IntegrityError as e:
        Logger.error(f"Database: Integrity error creating habit '{name}': {e}")
        raise
    except sqlite3.Error as e:
        Logger.error(f"Database: Error creating habit '{name}': {e}")
        raise


def get_all_habits(include_archived: bool = False) -> List[Habit]:
    """
    Retrieve all habits from the database.

    Args:
        include_archived: If True, includes archived habits. Default False.

    Returns:
        List[Habit]: List of Habit objects (Pydantic models)
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            if include_archived:
                cursor.execute(
                    """
                    SELECT id, name, color, goal_type, goal_count, created_at, archived
                    FROM habits
                    ORDER BY created_at DESC
                    """
                )
            else:
                cursor.execute(
                    """
                    SELECT id, name, color, goal_type, goal_count, created_at, archived
                    FROM habits
                    WHERE archived = 0
                    ORDER BY created_at DESC
                    """
                )

            rows = cursor.fetchall()
            habits = [Habit.from_db_row(dict(row)) for row in rows]
            Logger.info(
                f"Database: Retrieved {len(habits)} habit(s) (archived={include_archived})"
            )
            return habits
    except sqlite3.Error as e:
        Logger.error(f"Database: Error retrieving habits: {e}")
        return []


def get_habit_by_id(habit_id: int) -> Optional[Habit]:
    """
    Retrieve a single habit by ID.

    Args:
        habit_id: The habit ID to retrieve

    Returns:
        Habit | None: Habit object if found, None otherwise
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, color, goal_type, goal_count, created_at, archived
                FROM habits
                WHERE id = ?
                """,
                (habit_id,),
            )

            row = cursor.fetchone()
            if row:
                habit = Habit.from_db_row(dict(row))
                Logger.info(f"Database: Retrieved habit ID {habit_id}")
                return habit
            else:
                Logger.warning(f"Database: Habit ID {habit_id} not found")
                return None
    except sqlite3.Error as e:
        Logger.error(f"Database: Error retrieving habit ID {habit_id}: {e}")
        return None


def update_habit(habit_id: int, **kwargs) -> bool:
    """
    Update a habit's fields.

    Args:
        habit_id: The habit ID to update
        **kwargs: Field names and values to update
                 (name, color, goal_type, goal_count, archived)

    Returns:
        bool: True if update successful, False otherwise
    """
    # Filter out None values and invalid fields
    valid_fields = {"name", "color", "goal_type", "goal_count", "archived"}
    updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}

    if not updates:
        Logger.warning(f"Database: No valid fields to update for habit ID {habit_id}")
        return False

    # Build UPDATE query
    set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
    values = list(updates.values()) + [habit_id]

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                UPDATE habits
                SET {set_clause}
                WHERE id = ?
                """,
                values,
            )
            conn.commit()

            if cursor.rowcount > 0:
                Logger.info(f"Database: Updated habit ID {habit_id}: {updates}")
                return True
            else:
                Logger.warning(f"Database: Habit ID {habit_id} not found for update")
                return False
    except sqlite3.IntegrityError as e:
        Logger.error(f"Database: Integrity error updating habit ID {habit_id}: {e}")
        return False
    except sqlite3.Error as e:
        Logger.error(f"Database: Error updating habit ID {habit_id}: {e}")
        return False


def delete_habit(habit_id: int) -> bool:
    """
    Permanently delete a habit from the database.

    Note: This is a hard delete. For soft delete, use archive_habit() instead.

    Args:
        habit_id: The habit ID to delete

    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM habits
                WHERE id = ?
                """,
                (habit_id,),
            )
            conn.commit()

            if cursor.rowcount > 0:
                Logger.info(f"Database: Deleted habit ID {habit_id}")
                return True
            else:
                Logger.warning(f"Database: Habit ID {habit_id} not found for deletion")
                return False
    except sqlite3.Error as e:
        Logger.error(f"Database: Error deleting habit ID {habit_id}: {e}")
        return False


def archive_habit(habit_id: int) -> bool:
    """
    Archive a habit (soft delete).

    Archived habits are hidden from normal views but remain in database.

    Args:
        habit_id: The habit ID to archive

    Returns:
        bool: True if archival successful, False otherwise
    """
    return update_habit(habit_id, archived=True)


def unarchive_habit(habit_id: int) -> bool:
    """
    Restore an archived habit.

    Args:
        habit_id: The habit ID to unarchive

    Returns:
        bool: True if restoration successful, False otherwise
    """
    return update_habit(habit_id, archived=False)


# ============================================================================
# Completion Operations
# ============================================================================


def increment_completion(
    habit_id: int, completion_date: date, amount: int = 1
) -> Optional[Completion]:
    """
    Increment the completion count for a habit on a specific date.

    If a completion record exists for the date, increments the count.
    If no record exists, creates a new one with the given count.

    Uses UPSERT pattern (INSERT ... ON CONFLICT).

    Args:
        habit_id: The habit ID
        completion_date: The date of the completion
        amount: Amount to increment by (default 1)

    Returns:
        Completion | None: Updated/created Completion object, or None on error
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Convert date to ISO format string for Python 3.12+ compatibility
            date_str = completion_date.isoformat()

            # Use UPSERT to insert or update
            cursor.execute(
                """
                INSERT INTO completions (habit_id, date, count)
                VALUES (?, ?, ?)
                ON CONFLICT(habit_id, date)
                DO UPDATE SET count = count + ?
                """,
                (habit_id, date_str, amount, amount),
            )
            conn.commit()

            # Fetch the updated/created record
            cursor.execute(
                """
                SELECT id, habit_id, date, count, completed_at
                FROM completions
                WHERE habit_id = ? AND date = ?
                """,
                (habit_id, date_str),
            )

            row = cursor.fetchone()
            if row:
                completion = Completion.from_db_row(dict(row))
                Logger.info(
                    f"Database: Incremented completion for habit {habit_id} on {completion_date} (count={completion.count})"
                )
                return completion
            else:
                Logger.error(
                    f"Database: Failed to retrieve completion after increment"
                )
                return None
    except sqlite3.Error as e:
        Logger.error(
            f"Database: Error incrementing completion for habit {habit_id}: {e}"
        )
        return None


def decrement_completion(
    habit_id: int, completion_date: date, amount: int = 1
) -> Optional[Completion]:
    """
    Decrement the completion count for a habit on a specific date.

    If count reaches 0, the record is kept (not deleted) to maintain history.
    Count cannot go below 0.

    Args:
        habit_id: The habit ID
        completion_date: The date of the completion
        amount: Amount to decrement by (default 1)

    Returns:
        Completion | None: Updated Completion object, or None if record doesn't exist or error
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Convert date to ISO format string for Python 3.12+ compatibility
            date_str = completion_date.isoformat()

            # Update count, ensuring it doesn't go below 0
            cursor.execute(
                """
                UPDATE completions
                SET count = MAX(0, count - ?)
                WHERE habit_id = ? AND date = ?
                """,
                (amount, habit_id, date_str),
            )
            conn.commit()

            if cursor.rowcount == 0:
                Logger.warning(
                    f"Database: No completion found for habit {habit_id} on {completion_date}"
                )
                return None

            # Fetch the updated record
            cursor.execute(
                """
                SELECT id, habit_id, date, count, completed_at
                FROM completions
                WHERE habit_id = ? AND date = ?
                """,
                (habit_id, date_str),
            )

            row = cursor.fetchone()
            if row:
                completion = Completion.from_db_row(dict(row))
                Logger.info(
                    f"Database: Decremented completion for habit {habit_id} on {completion_date} (count={completion.count})"
                )
                return completion
            else:
                return None
    except sqlite3.Error as e:
        Logger.error(
            f"Database: Error decrementing completion for habit {habit_id}: {e}"
        )
        return None


def get_completion_for_date(
    habit_id: int, completion_date: date
) -> Optional[Completion]:
    """
    Retrieve a single completion record for a habit on a specific date.

    Args:
        habit_id: The habit ID
        completion_date: The date to query

    Returns:
        Completion | None: Completion object if found, None otherwise
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Convert date to ISO format string for Python 3.12+ compatibility
            date_str = completion_date.isoformat()
            cursor.execute(
                """
                SELECT id, habit_id, date, count, completed_at
                FROM completions
                WHERE habit_id = ? AND date = ?
                """,
                (habit_id, date_str),
            )

            row = cursor.fetchone()
            if row:
                completion = Completion.from_db_row(dict(row))
                Logger.info(
                    f"Database: Retrieved completion for habit {habit_id} on {completion_date}"
                )
                return completion
            else:
                return None
    except sqlite3.Error as e:
        Logger.error(
            f"Database: Error retrieving completion for habit {habit_id}: {e}"
        )
        return None


def get_completions_for_habit(
    habit_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None
) -> List[Completion]:
    """
    Retrieve all completions for a habit, optionally filtered by date range.

    Args:
        habit_id: The habit ID
        start_date: Optional start date (inclusive)
        end_date: Optional end date (inclusive)

    Returns:
        List[Completion]: List of Completion objects, ordered by date descending
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Convert dates to ISO format strings for Python 3.12+ compatibility
            start_str = start_date.isoformat() if start_date else None
            end_str = end_date.isoformat() if end_date else None

            if start_str and end_str:
                cursor.execute(
                    """
                    SELECT id, habit_id, date, count, completed_at
                    FROM completions
                    WHERE habit_id = ? AND date BETWEEN ? AND ?
                    ORDER BY date DESC
                    """,
                    (habit_id, start_str, end_str),
                )
            elif start_str:
                cursor.execute(
                    """
                    SELECT id, habit_id, date, count, completed_at
                    FROM completions
                    WHERE habit_id = ? AND date >= ?
                    ORDER BY date DESC
                    """,
                    (habit_id, start_str),
                )
            elif end_str:
                cursor.execute(
                    """
                    SELECT id, habit_id, date, count, completed_at
                    FROM completions
                    WHERE habit_id = ? AND date <= ?
                    ORDER BY date DESC
                    """,
                    (habit_id, end_str),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, habit_id, date, count, completed_at
                    FROM completions
                    WHERE habit_id = ?
                    ORDER BY date DESC
                    """,
                    (habit_id,),
                )

            rows = cursor.fetchall()
            completions = [Completion.from_db_row(dict(row)) for row in rows]
            Logger.info(
                f"Database: Retrieved {len(completions)} completion(s) for habit {habit_id}"
            )
            return completions
    except sqlite3.Error as e:
        Logger.error(
            f"Database: Error retrieving completions for habit {habit_id}: {e}"
        )
        return []


def get_completions_for_date_range(
    start_date: date, end_date: date
) -> Dict[int, List[Completion]]:
    """
    Retrieve all completions across all habits for a date range.

    Useful for weekly/monthly views that show multiple habits.

    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)

    Returns:
        Dict[int, List[Completion]]: Dictionary mapping habit_id to list of Completions
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Convert dates to ISO format strings for Python 3.12+ compatibility
            start_str = start_date.isoformat()
            end_str = end_date.isoformat()
            cursor.execute(
                """
                SELECT id, habit_id, date, count, completed_at
                FROM completions
                WHERE date BETWEEN ? AND ?
                ORDER BY habit_id, date DESC
                """,
                (start_str, end_str),
            )

            rows = cursor.fetchall()
            completions_by_habit: Dict[int, List[Completion]] = {}

            for row in rows:
                completion = Completion.from_db_row(dict(row))
                if completion.habit_id not in completions_by_habit:
                    completions_by_habit[completion.habit_id] = []
                completions_by_habit[completion.habit_id].append(completion)

            Logger.info(
                f"Database: Retrieved completions for {len(completions_by_habit)} habit(s) in date range"
            )
            return completions_by_habit
    except sqlite3.Error as e:
        Logger.error(f"Database: Error retrieving completions for date range: {e}")
        return {}


# ============================================
# SETTINGS CRUD OPERATIONS
# ============================================


def get_setting(key: str) -> Optional[str]:
    """
    Get a setting value by key.

    Args:
        key: Setting key to retrieve

    Returns:
        Optional[str]: Setting value if found, None otherwise
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                Logger.debug(f"Database: Retrieved setting '{key}' = '{row[0]}'")
                return row[0]
            Logger.debug(f"Database: Setting '{key}' not found")
            return None
    except sqlite3.Error as e:
        Logger.error(f"Database: Error retrieving setting '{key}': {e}")
        return None


def set_setting(key: str, value: str) -> bool:
    """
    Set a setting value (insert or update).

    Args:
        key: Setting key
        value: Setting value

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, value),
            )
            conn.commit()
            Logger.info(f"Database: Set setting '{key}' = '{value}'")
            return True
    except sqlite3.Error as e:
        Logger.error(f"Database: Error setting '{key}': {e}")
        return False


def get_all_settings() -> Dict[str, str]:
    """
    Get all settings as a dictionary.

    Returns:
        Dict[str, str]: Dictionary of all settings (key: value)
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            rows = cursor.fetchall()
            settings = {row[0]: row[1] for row in rows}
            Logger.info(f"Database: Retrieved {len(settings)} settings")
            return settings
    except sqlite3.Error as e:
        Logger.error(f"Database: Error retrieving all settings: {e}")
        return {}
