"""
Unit Tests for Database Operations

Tests all CRUD operations for habits, completions, and settings.
Uses in-memory SQLite database for fast, isolated tests.
"""

import pytest
import sys
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add app directory to path for imports
app_dir = Path(__file__).parent.parent.parent.parent / "app"
sys.path.insert(0, str(app_dir))

# Import database module after path setup
from models import database
from models.schemas import Habit, Completion


@pytest.mark.database
class TestHabitCRUD:
    """Test Create, Read, Update, Delete operations for habits."""

    def test_create_habit_success(self, test_db):
        """Creating a valid habit should return habit ID."""
        with patch.object(database, 'get_connection', return_value=test_db):
            habit_id = database.create_habit(
                name='Exercise',
                color='#E57373',
                goal_type='daily',
                goal_count=1
            )

            assert habit_id > 0

            # Verify it was created
            cursor = test_db.cursor()
            cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
            row = cursor.fetchone()

            assert row is not None
            assert row['name'] == 'Exercise'
            assert row['color'] == '#E57373'
            assert row['goal_type'] == 'daily'
            assert row['goal_count'] == 1
            assert row['archived'] == 0

    def test_create_habit_duplicate_name_fails(self, test_db):
        """Creating habit with duplicate name should raise IntegrityError."""
        with patch.object(database, 'get_connection', return_value=test_db):
            # Create first habit
            database.create_habit('Exercise', '#E57373', 'daily', 1)

            # Attempt to create duplicate
            with pytest.raises(sqlite3.IntegrityError):
                database.create_habit('Exercise', '#64B5F6', 'weekly', 3)

    def test_create_habit_case_insensitive_duplicate_fails(self, test_db):
        """Duplicate name with different case should also fail."""
        with patch.object(database, 'get_connection', return_value=test_db):
            database.create_habit('Exercise', '#E57373', 'daily', 1)

            # Different case should still violate unique constraint
            with pytest.raises(sqlite3.IntegrityError):
                database.create_habit('EXERCISE', '#64B5F6', 'weekly', 3)

    def test_get_all_habits_empty(self, test_db):
        """Get all habits from empty database should return empty list."""
        with patch.object(database, 'get_connection', return_value=test_db):
            habits = database.get_all_habits()
            assert habits == []

    def test_get_all_habits_returns_all_active(self, test_db, create_test_habit):
        """Get all habits should return all non-archived habits."""
        # Create test habits directly in test_db
        create_test_habit('Habit 1', '#E57373', 'daily', 1)
        create_test_habit('Habit 2', '#64B5F6', 'weekly', 3)
        create_test_habit('Habit 3', '#81C784', 'monthly', 20, archived=1)

        with patch.object(database, 'get_connection', return_value=test_db):
            habits = database.get_all_habits(include_archived=False)

            assert len(habits) == 2
            assert all(isinstance(h, Habit) for h in habits)
            assert all(h.archived == 0 for h in habits)

    def test_get_all_habits_includes_archived(self, test_db, create_test_habit):
        """Get all habits with include_archived should return all habits."""
        create_test_habit('Habit 1', '#E57373', 'daily', 1)
        create_test_habit('Habit 2', '#64B5F6', 'weekly', 3, archived=1)

        with patch.object(database, 'get_connection', return_value=test_db):
            habits = database.get_all_habits(include_archived=True)

            assert len(habits) == 2

    def test_get_habit_by_id_found(self, test_db, create_test_habit):
        """Get habit by ID should return Habit object."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)

        with patch.object(database, 'get_connection', return_value=test_db):
            habit = database.get_habit_by_id(habit_id)

            assert habit is not None
            assert isinstance(habit, Habit)
            assert habit.id == habit_id
            assert habit.name == 'Exercise'

    def test_get_habit_by_id_not_found(self, test_db):
        """Get habit by non-existent ID should return None."""
        with patch.object(database, 'get_connection', return_value=test_db):
            habit = database.get_habit_by_id(99999)
            assert habit is None

    def test_update_habit_name(self, test_db, create_test_habit):
        """Updating habit name should work."""
        habit_id = create_test_habit('Old Name', '#E57373', 'daily', 1)

        with patch.object(database, 'get_connection', return_value=test_db):
            result = database.update_habit(habit_id, name='New Name')
            assert result is True

            # Verify update
            habit = database.get_habit_by_id(habit_id)
            assert habit.name == 'New Name'

    def test_update_habit_multiple_fields(self, test_db, create_test_habit):
        """Updating multiple fields should work."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)

        with patch.object(database, 'get_connection', return_value=test_db):
            result = database.update_habit(
                habit_id,
                name='Workout',
                color='#64B5F6',
                goal_type='weekly',
                goal_count=3
            )
            assert result is True

            # Verify all updates
            habit = database.get_habit_by_id(habit_id)
            assert habit.name == 'Workout'
            assert habit.color == '#64B5F6'
            assert habit.goal_type == 'weekly'
            assert habit.goal_count == 3

    def test_update_habit_nonexistent(self, test_db):
        """Updating non-existent habit should return False."""
        with patch.object(database, 'get_connection', return_value=test_db):
            result = database.update_habit(99999, name='Test')
            assert result is False

    def test_update_habit_no_fields(self, test_db, create_test_habit):
        """Updating with no valid fields should return False."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)

        with patch.object(database, 'get_connection', return_value=test_db):
            result = database.update_habit(habit_id)
            assert result is False

    def test_delete_habit_success(self, test_db, create_test_habit):
        """Deleting an existing habit should work."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)

        with patch.object(database, 'get_connection', return_value=test_db):
            result = database.delete_habit(habit_id)
            assert result is True

            # Verify deletion
            habit = database.get_habit_by_id(habit_id)
            assert habit is None

    def test_delete_habit_nonexistent(self, test_db):
        """Deleting non-existent habit should return False."""
        with patch.object(database, 'get_connection', return_value=test_db):
            result = database.delete_habit(99999)
            assert result is False

    def test_delete_habit_cascades_completions(self, test_db, create_test_habit, create_test_completion):
        """Deleting habit should cascade delete completions."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)
        create_test_completion(habit_id, date(2024, 12, 15), 5)

        # Enable foreign keys for cascade test
        test_db.execute("PRAGMA foreign_keys = ON")

        with patch.object(database, 'get_connection', return_value=test_db):
            database.delete_habit(habit_id)

            # Verify completions were deleted
            cursor = test_db.cursor()
            cursor.execute("SELECT COUNT(*) FROM completions WHERE habit_id = ?", (habit_id,))
            count = cursor.fetchone()[0]
            assert count == 0

    def test_archive_habit_success(self, test_db, create_test_habit):
        """Archiving a habit should set archived flag."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)

        with patch.object(database, 'get_connection', return_value=test_db):
            result = database.archive_habit(habit_id)
            assert result is True

            # Verify archive
            habit = database.get_habit_by_id(habit_id)
            assert habit.archived == 1

    def test_unarchive_habit_success(self, test_db, create_test_habit):
        """Unarchiving a habit should clear archived flag."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1, archived=1)

        with patch.object(database, 'get_connection', return_value=test_db):
            result = database.unarchive_habit(habit_id)
            assert result is True

            # Verify unarchive
            habit = database.get_habit_by_id(habit_id)
            assert habit.archived == 0


@pytest.mark.database
class TestCompletionOperations:
    """Test completion tracking operations."""

    def test_increment_completion_new_record(self, test_db, create_test_habit):
        """Incrementing completion for new date should create record."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)
        test_date = date(2024, 12, 15)

        with patch.object(database, 'get_connection', return_value=test_db):
            completion = database.increment_completion(habit_id, test_date, 1)

            assert completion is not None
            assert isinstance(completion, Completion)
            assert completion.habit_id == habit_id
            assert completion.date == test_date
            assert completion.count == 1

    def test_increment_completion_existing_record(self, test_db, create_test_habit, create_test_completion):
        """Incrementing completion for existing date should add to count."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)
        test_date = date(2024, 12, 15)
        create_test_completion(habit_id, test_date, 5)

        with patch.object(database, 'get_connection', return_value=test_db):
            completion = database.increment_completion(habit_id, test_date, 3)

            assert completion is not None
            assert completion.count == 8  # 5 + 3

    def test_increment_completion_large_amount(self, test_db, create_test_habit):
        """Incrementing by large amount should work."""
        habit_id = create_test_habit('Read', '#64B5F6', 'daily', 30)
        test_date = date(2024, 12, 15)

        with patch.object(database, 'get_connection', return_value=test_db):
            completion = database.increment_completion(habit_id, test_date, 45)

            assert completion.count == 45

    def test_decrement_completion_success(self, test_db, create_test_habit, create_test_completion):
        """Decrementing completion should reduce count."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)
        test_date = date(2024, 12, 15)
        create_test_completion(habit_id, test_date, 10)

        with patch.object(database, 'get_connection', return_value=test_db):
            completion = database.decrement_completion(habit_id, test_date, 3)

            assert completion is not None
            assert completion.count == 7

    def test_decrement_completion_to_zero(self, test_db, create_test_habit, create_test_completion):
        """Decrementing to zero should keep record at 0."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)
        test_date = date(2024, 12, 15)
        create_test_completion(habit_id, test_date, 5)

        with patch.object(database, 'get_connection', return_value=test_db):
            completion = database.decrement_completion(habit_id, test_date, 10)

            assert completion is not None
            assert completion.count == 0  # Can't go below 0

    def test_decrement_completion_nonexistent(self, test_db, create_test_habit):
        """Decrementing non-existent completion should return None."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)
        test_date = date(2024, 12, 15)

        with patch.object(database, 'get_connection', return_value=test_db):
            completion = database.decrement_completion(habit_id, test_date, 1)
            assert completion is None

    def test_get_completion_for_date_found(self, test_db, create_test_habit, create_test_completion):
        """Get completion for date should return Completion object."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)
        test_date = date(2024, 12, 15)
        create_test_completion(habit_id, test_date, 5)

        with patch.object(database, 'get_connection', return_value=test_db):
            completion = database.get_completion_for_date(habit_id, test_date)

            assert completion is not None
            assert completion.habit_id == habit_id
            assert completion.date == test_date
            assert completion.count == 5

    def test_get_completion_for_date_not_found(self, test_db, create_test_habit):
        """Get completion for non-existent date should return None."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)

        with patch.object(database, 'get_connection', return_value=test_db):
            completion = database.get_completion_for_date(habit_id, date(2024, 12, 15))
            assert completion is None

    def test_get_completions_for_habit_all(self, test_db, create_test_habit, create_test_completion):
        """Get all completions for habit should return list."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)
        create_test_completion(habit_id, date(2024, 12, 13), 1)
        create_test_completion(habit_id, date(2024, 12, 14), 2)
        create_test_completion(habit_id, date(2024, 12, 15), 3)

        with patch.object(database, 'get_connection', return_value=test_db):
            completions = database.get_completions_for_habit(habit_id)

            assert len(completions) == 3
            assert all(isinstance(c, Completion) for c in completions)
            # Should be ordered by date descending
            assert completions[0].date == date(2024, 12, 15)
            assert completions[2].date == date(2024, 12, 13)

    def test_get_completions_for_habit_with_date_range(self, test_db, create_test_habit, create_test_completion):
        """Get completions with date filter should only return matching."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)
        create_test_completion(habit_id, date(2024, 12, 10), 1)
        create_test_completion(habit_id, date(2024, 12, 15), 2)
        create_test_completion(habit_id, date(2024, 12, 20), 3)

        with patch.object(database, 'get_connection', return_value=test_db):
            completions = database.get_completions_for_habit(
                habit_id,
                start_date=date(2024, 12, 14),
                end_date=date(2024, 12, 18)
            )

            assert len(completions) == 1
            assert completions[0].date == date(2024, 12, 15)

    def test_get_completions_for_date_range(self, test_db, create_test_habit, create_test_completion):
        """Get completions for date range across habits."""
        habit1 = create_test_habit('Exercise', '#E57373', 'daily', 1)
        habit2 = create_test_habit('Read', '#64B5F6', 'daily', 30)

        create_test_completion(habit1, date(2024, 12, 15), 1)
        create_test_completion(habit1, date(2024, 12, 16), 1)
        create_test_completion(habit2, date(2024, 12, 15), 20)
        create_test_completion(habit2, date(2024, 12, 20), 30)  # Out of range

        with patch.object(database, 'get_connection', return_value=test_db):
            result = database.get_completions_for_date_range(
                date(2024, 12, 15),
                date(2024, 12, 18)
            )

            assert len(result) == 2  # Two habits
            assert habit1 in result
            assert habit2 in result
            assert len(result[habit1]) == 2
            assert len(result[habit2]) == 1

    def test_get_completions_for_date_range_empty(self, test_db):
        """Get completions for empty date range should return empty dict."""
        with patch.object(database, 'get_connection', return_value=test_db):
            result = database.get_completions_for_date_range(
                date(2024, 12, 1),
                date(2024, 12, 31)
            )
            assert result == {}


@pytest.mark.database
class TestSettingsOperations:
    """Test settings CRUD operations."""

    def test_get_setting_exists(self, test_db):
        """Get existing setting should return value."""
        # Insert setting directly
        test_db.execute("INSERT INTO settings (key, value) VALUES ('test', 'value')", ())
        test_db.commit()

        with patch.object(database, 'get_connection', return_value=test_db):
            value = database.get_setting('test')
            assert value == 'value'

    def test_get_setting_not_exists(self, test_db):
        """Get non-existent setting should return None."""
        with patch.object(database, 'get_connection', return_value=test_db):
            value = database.get_setting('nonexistent')
            assert value is None

    def test_set_setting_new(self, test_db):
        """Setting new key should insert."""
        with patch.object(database, 'get_connection', return_value=test_db):
            result = database.set_setting('new_key', 'new_value')
            assert result is True

            # Verify insertion
            value = database.get_setting('new_key')
            assert value == 'new_value'

    def test_set_setting_update(self, test_db):
        """Setting existing key should update."""
        test_db.execute("INSERT INTO settings (key, value) VALUES ('key', 'old')", ())
        test_db.commit()

        with patch.object(database, 'get_connection', return_value=test_db):
            result = database.set_setting('key', 'new')
            assert result is True

            # Verify update
            value = database.get_setting('key')
            assert value == 'new'

    def test_get_all_settings_empty(self, test_db):
        """Get all settings from empty table should return empty dict."""
        # Delete default language setting
        test_db.execute("DELETE FROM settings", ())
        test_db.commit()

        with patch.object(database, 'get_connection', return_value=test_db):
            settings = database.get_all_settings()
            assert settings == {}

    def test_get_all_settings_multiple(self, test_db):
        """Get all settings should return dict of all settings."""
        test_db.execute("DELETE FROM settings", ())
        test_db.execute("INSERT INTO settings (key, value) VALUES ('key1', 'value1')", ())
        test_db.execute("INSERT INTO settings (key, value) VALUES ('key2', 'value2')", ())
        test_db.commit()

        with patch.object(database, 'get_connection', return_value=test_db):
            settings = database.get_all_settings()

            assert len(settings) == 2
            assert settings['key1'] == 'value1'
            assert settings['key2'] == 'value2'


@pytest.mark.database
class TestDatabaseConstraints:
    """Test database constraints and integrity."""

    def test_habit_goal_type_constraint(self, test_db):
        """Invalid goal_type should violate CHECK constraint."""
        with patch.object(database, 'get_connection', return_value=test_db):
            with pytest.raises(sqlite3.IntegrityError):
                database.create_habit('Test', '#E57373', 'yearly', 1)

    def test_habit_goal_count_min_constraint(self, test_db):
        """Goal count less than 1 should violate CHECK constraint."""
        with patch.object(database, 'get_connection', return_value=test_db):
            with pytest.raises(sqlite3.IntegrityError):
                database.create_habit('Test', '#E57373', 'daily', 0)

    def test_habit_goal_count_max_constraint(self, test_db):
        """Goal count greater than 100 should violate CHECK constraint."""
        with patch.object(database, 'get_connection', return_value=test_db):
            with pytest.raises(sqlite3.IntegrityError):
                database.create_habit('Test', '#E57373', 'daily', 101)

    def test_completion_unique_constraint(self, test_db, create_test_habit):
        """Creating duplicate completion for same date should fail."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)
        test_date = date(2024, 12, 15)

        # Insert first completion directly
        cursor = test_db.cursor()
        cursor.execute(
            "INSERT INTO completions (habit_id, date, count) VALUES (?, ?, ?)",
            (habit_id, test_date.isoformat(), 5)
        )
        test_db.commit()

        # Try to insert duplicate directly (bypass UPSERT logic)
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                "INSERT INTO completions (habit_id, date, count) VALUES (?, ?, ?)",
                (habit_id, test_date.isoformat(), 10)
            )


@pytest.mark.database
class TestDatabaseEdgeCases:
    """Test edge cases and unusual inputs."""

    def test_habit_with_special_characters(self, test_db):
        """Habit names with special characters should work."""
        with patch.object(database, 'get_connection', return_value=test_db):
            habit_id = database.create_habit(
                name="Read 'War & Peace'",
                color='#E57373',
                goal_type='daily',
                goal_count=1
            )

            habit = database.get_habit_by_id(habit_id)
            assert habit.name == "Read 'War & Peace'"

    def test_completion_date_boundaries(self, test_db, create_test_habit):
        """Completions should work with edge case dates."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)

        with patch.object(database, 'get_connection', return_value=test_db):
            # Very old date
            old_date = date(1900, 1, 1)
            completion1 = database.increment_completion(habit_id, old_date, 1)
            assert completion1 is not None

            # Recent past date
            past_date = date(2020, 6, 15)
            completion2 = database.increment_completion(habit_id, past_date, 1)
            assert completion2 is not None

    def test_get_completions_reverse_date_range(self, test_db, create_test_habit, create_test_completion):
        """Query with reversed date range (end < start) should return empty."""
        habit_id = create_test_habit('Exercise', '#E57373', 'daily', 1)
        create_test_completion(habit_id, date(2024, 12, 15), 1)

        with patch.object(database, 'get_connection', return_value=test_db):
            completions = database.get_completions_for_habit(
                habit_id,
                start_date=date(2024, 12, 20),
                end_date=date(2024, 12, 10)
            )
            assert len(completions) == 0
