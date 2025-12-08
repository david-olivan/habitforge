"""
Database Operations for HabitForge

This module handles all SQLite database operations for habits.
Uses context managers for safe connection handling.
"""

import sqlite3
import os
from typing import List, Dict, Optional
from pathlib import Path
from .schemas import Habit
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