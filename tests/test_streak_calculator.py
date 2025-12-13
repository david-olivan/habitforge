"""
Unit Tests for Streak Calculator

Tests the streak tracking logic for habit completion streaks.
"""

import sys
import pytest
from datetime import date, timedelta
from pathlib import Path

# Add app directory to path for imports
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

from logic.streak_calculator import calculate_streak, get_previous_period_start
from models.database import (
    init_database,
    create_habit,
    increment_completion,
    delete_habit,
    get_connection
)


# Fixtures
@pytest.fixture(scope="function")
def setup_database():
    """Initialize a fresh test database for each test."""
    init_database()
    yield
    # Cleanup: Delete all test data after each test
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM completions")
        cursor.execute("DELETE FROM habits")
        conn.commit()


# Tests for get_previous_period_start()
class TestGetPreviousPeriodStart:
    """Test the get_previous_period_start function."""

    def test_daily_previous_period(self):
        """Daily goal type should return yesterday."""
        test_date = date(2024, 12, 13)  # Friday
        result = get_previous_period_start(test_date, "daily")
        expected = date(2024, 12, 12)  # Thursday
        assert result == expected, f"Expected {expected}, got {result}"

    def test_weekly_previous_period_friday(self):
        """Weekly goal type should return Monday of previous week (from Friday)."""
        test_date = date(2024, 12, 13)  # Friday in week Dec 9-15
        result = get_previous_period_start(test_date, "weekly")
        expected = date(2024, 12, 2)  # Monday of previous week (Dec 2-8)
        assert result == expected, f"Expected {expected}, got {result}"

    def test_weekly_previous_period_monday(self):
        """Weekly goal type should return Monday of previous week (from Monday)."""
        test_date = date(2024, 12, 9)  # Monday
        result = get_previous_period_start(test_date, "weekly")
        expected = date(2024, 12, 2)  # Monday of previous week
        assert result == expected, f"Expected {expected}, got {result}"

    def test_weekly_previous_period_sunday(self):
        """Weekly goal type should return Monday of previous week (from Sunday)."""
        test_date = date(2024, 12, 15)  # Sunday
        result = get_previous_period_start(test_date, "weekly")
        expected = date(2024, 12, 2)  # Monday of previous week
        assert result == expected, f"Expected {expected}, got {result}"

    def test_monthly_previous_period_mid_month(self):
        """Monthly goal type should return 1st of previous month (from mid-month)."""
        test_date = date(2024, 12, 13)  # December 13
        result = get_previous_period_start(test_date, "monthly")
        expected = date(2024, 11, 1)  # November 1
        assert result == expected, f"Expected {expected}, got {result}"

    def test_monthly_previous_period_first_day(self):
        """Monthly goal type should return 1st of previous month (from 1st)."""
        test_date = date(2024, 12, 1)  # December 1
        result = get_previous_period_start(test_date, "monthly")
        expected = date(2024, 11, 1)  # November 1
        assert result == expected, f"Expected {expected}, got {result}"

    def test_monthly_previous_period_last_day(self):
        """Monthly goal type should return 1st of previous month (from last day)."""
        test_date = date(2024, 12, 31)  # December 31
        result = get_previous_period_start(test_date, "monthly")
        expected = date(2024, 11, 1)  # November 1
        assert result == expected, f"Expected {expected}, got {result}"

    def test_monthly_previous_period_january(self):
        """Monthly goal type should handle year rollover correctly."""
        test_date = date(2025, 1, 15)  # January 2025
        result = get_previous_period_start(test_date, "monthly")
        expected = date(2024, 12, 1)  # December 2024
        assert result == expected, f"Expected {expected}, got {result}"

    def test_invalid_goal_type_raises_error(self):
        """Invalid goal type should raise ValueError."""
        test_date = date(2024, 12, 13)
        with pytest.raises(ValueError, match="Invalid goal_type"):
            get_previous_period_start(test_date, "yearly")


# Tests for calculate_streak()
class TestCalculateStreak:
    """Test the calculate_streak function."""

    def test_new_habit_no_completions(self, setup_database):
        """New habit with no completions should have streak = 0."""
        habit_id = create_habit("Test Habit", "#E57373", "daily", 1)
        streak = calculate_streak(habit_id, "daily", 1)
        assert streak == 0, f"Expected streak 0 for new habit, got {streak}"

    def test_current_period_only_not_counted(self, setup_database):
        """Completions only in current period should not count toward streak."""
        habit_id = create_habit("Test Daily", "#FFB74D", "daily", 3)
        today = date.today()

        # Complete today's goal (current period)
        increment_completion(habit_id, today, 3)

        streak = calculate_streak(habit_id, "daily", 3)
        assert streak == 0, f"Current period should not count, expected 0 got {streak}"

    def test_one_previous_period_complete(self, setup_database):
        """One complete previous period should give streak = 1."""
        habit_id = create_habit("Test Daily", "#FFF176", "daily", 2)
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Complete yesterday's goal
        increment_completion(habit_id, yesterday, 2)

        streak = calculate_streak(habit_id, "daily", 2)
        assert streak == 1, f"Expected streak 1 with one complete previous period, got {streak}"

    def test_multiple_consecutive_daily_periods(self, setup_database):
        """Multiple consecutive complete days should count correctly."""
        habit_id = create_habit("Test Daily", "#81C784", "daily", 1)
        today = date.today()

        # Complete last 5 days (not including today)
        for days_ago in range(1, 6):
            completion_date = today - timedelta(days=days_ago)
            increment_completion(habit_id, completion_date, 1)

        streak = calculate_streak(habit_id, "daily", 1)
        assert streak == 5, f"Expected streak 5 with 5 consecutive days, got {streak}"

    def test_broken_streak_stops_at_incomplete(self, setup_database):
        """Streak should stop at first incomplete period."""
        habit_id = create_habit("Test Daily", "#4DB6AC", "daily", 2)
        today = date.today()

        # Days 1-9 ago: complete (2/2)
        for days_ago in range(1, 10):
            completion_date = today - timedelta(days=days_ago)
            increment_completion(habit_id, completion_date, 2)

        # Day 10 ago: incomplete (0/2) - breaks streak
        # (implicitly incomplete by not adding completions)

        streak = calculate_streak(habit_id, "daily", 2)
        assert streak == 9, f"Expected streak 9 (stopped at day 10), got {streak}"

    def test_partial_completion_breaks_streak(self, setup_database):
        """Partial completion (less than goal) should break streak."""
        habit_id = create_habit("Test Daily", "#64B5F6", "daily", 5)
        today = date.today()

        # 3 days ago: incomplete (only 3/5)
        three_days_ago = today - timedelta(days=3)
        increment_completion(habit_id, three_days_ago, 3)

        # 2 days ago: complete (5/5)
        two_days_ago = today - timedelta(days=2)
        increment_completion(habit_id, two_days_ago, 5)

        # Yesterday: complete (5/5)
        yesterday = today - timedelta(days=1)
        increment_completion(habit_id, yesterday, 5)

        streak = calculate_streak(habit_id, "daily", 5)
        assert streak == 2, f"Expected streak 2 (broken at 3 days ago), got {streak}"

    def test_over_completion_counts_as_complete(self, setup_database):
        """Completing more than goal should still count as complete."""
        habit_id = create_habit("Test Daily", "#BA68C8", "daily", 3)
        today = date.today()

        # Yesterday: over-complete (5/3)
        yesterday = today - timedelta(days=1)
        increment_completion(habit_id, yesterday, 5)

        streak = calculate_streak(habit_id, "daily", 3)
        assert streak == 1, f"Expected streak 1 with over-completion, got {streak}"

    def test_weekly_streak_calculation(self, setup_database):
        """Weekly habits should count consecutive weeks."""
        habit_id = create_habit("Test Weekly", "#F06292", "weekly", 5)
        today = date.today()

        # Get Monday of current week
        current_monday = today - timedelta(days=today.weekday())

        # Complete last 3 weeks (not current week)
        for weeks_ago in range(1, 4):
            # Add completions in previous weeks
            week_start = current_monday - timedelta(weeks=weeks_ago)
            # Add 5 completions spread across the week
            for day_offset in [0, 2, 4, 6]:  # Mon, Wed, Fri, Sun
                completion_date = week_start + timedelta(days=day_offset)
                increment_completion(habit_id, completion_date, 2 if day_offset == 0 else 1)

        streak = calculate_streak(habit_id, "weekly", 5)
        # Should have streak of 3 (last 3 weeks complete)
        assert streak == 3, f"Expected streak 3 for weekly habit, got {streak}"

    def test_monthly_streak_calculation(self, setup_database):
        """Monthly habits should count consecutive months."""
        habit_id = create_habit("Test Monthly", "#E57373", "monthly", 10)
        today = date.today()

        # Get first day of current month
        current_month_start = today.replace(day=1)

        # Complete last 2 months (not current month)
        for months_ago in range(1, 3):
            # Calculate the first day of the target month
            if months_ago == 1:
                month_start = current_month_start.replace(month=current_month_start.month - 1)
                if current_month_start.month == 1:
                    month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
            else:  # months_ago == 2
                month_start = current_month_start.replace(month=current_month_start.month - 2)
                if current_month_start.month <= 2:
                    month_start = current_month_start.replace(
                        year=current_month_start.year - 1,
                        month=12 + current_month_start.month - 2
                    )

            # Add completions throughout the month
            for day in [5, 10, 15, 20, 25]:
                completion_date = month_start.replace(day=day)
                increment_completion(habit_id, completion_date, 2)

        streak = calculate_streak(habit_id, "monthly", 10)
        # Should have streak of 2 (last 2 months complete)
        assert streak == 2, f"Expected streak 2 for monthly habit, got {streak}"

    def test_current_period_complete_not_counted(self, setup_database):
        """Even if current period is complete, it should not count toward streak."""
        habit_id = create_habit("Test Daily", "#FFB74D", "daily", 2)
        today = date.today()

        # Complete today (current period)
        increment_completion(habit_id, today, 2)

        # Complete yesterday
        yesterday = today - timedelta(days=1)
        increment_completion(habit_id, yesterday, 2)

        streak = calculate_streak(habit_id, "daily", 2)
        # Should only count yesterday, not today
        assert streak == 1, f"Current period should not count, expected 1 got {streak}"

    def test_zero_goal_count_handled_gracefully(self, setup_database):
        """Zero goal count edge case (should not happen but handle gracefully)."""
        habit_id = create_habit("Test Edge", "#81C784", "daily", 1)

        # Call with goal_count = 0 (edge case)
        streak = calculate_streak(habit_id, "daily", 0)
        # With goal 0, any completions meet the goal, so streak could be infinite
        # But we expect it to handle gracefully and not crash
        assert isinstance(streak, int), "Streak should return an integer"


# Integration test
class TestStreakCalculatorIntegration:
    """Integration tests for streak calculator."""

    def test_realistic_daily_habit_scenario(self, setup_database):
        """Test a realistic scenario: user builds a 7-day streak, breaks it, then builds 3-day."""
        habit_id = create_habit("Meditation", "#4DB6AC", "daily", 1)
        today = date.today()

        # Build 7-day streak (days 10-4 ago)
        for days_ago in range(10, 3, -1):
            completion_date = today - timedelta(days=days_ago)
            increment_completion(habit_id, completion_date, 1)

        # Day 3 ago: miss (breaks streak)
        # (no completion added)

        # Build 2-day streak (days 2-1 ago)
        for days_ago in range(2, 0, -1):
            completion_date = today - timedelta(days=days_ago)
            increment_completion(habit_id, completion_date, 1)

        streak = calculate_streak(habit_id, "daily", 1)
        # Should only count the recent 2-day streak (broken at day 3)
        assert streak == 2, f"Expected streak 2 after break, got {streak}"

    def test_multiple_habits_independent_streaks(self, setup_database):
        """Multiple habits should have independent streaks."""
        habit1_id = create_habit("Exercise", "#E57373", "daily", 1)
        habit2_id = create_habit("Reading", "#64B5F6", "daily", 1)
        today = date.today()

        # Habit 1: 5-day streak
        for days_ago in range(1, 6):
            completion_date = today - timedelta(days=days_ago)
            increment_completion(habit1_id, completion_date, 1)

        # Habit 2: 3-day streak
        for days_ago in range(1, 4):
            completion_date = today - timedelta(days=days_ago)
            increment_completion(habit2_id, completion_date, 1)

        streak1 = calculate_streak(habit1_id, "daily", 1)
        streak2 = calculate_streak(habit2_id, "daily", 1)

        assert streak1 == 5, f"Habit 1 expected streak 5, got {streak1}"
        assert streak2 == 3, f"Habit 2 expected streak 3, got {streak2}"


if __name__ == "__main__":
    # Allow running tests directly with: python test_streak_calculator.py
    pytest.main([__file__, "-v"])