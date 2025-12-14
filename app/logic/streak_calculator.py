"""
Streak Calculation for HabitForge

This module calculates consecutive periods of goal completion (streaks)
for habits. Streaks count backward from the current period (included if goal met)
until an incomplete period is found.
"""

from datetime import date, timedelta
from typing import Literal, Optional
from dateutil.relativedelta import relativedelta
from kivy.logger import Logger

from models.database import get_completions_for_habit
from logic.date_utils import get_period_boundaries, get_today


def calculate_streak(
    habit_id: int,
    goal_type: Literal["daily", "weekly", "monthly"],
    goal_count: int
) -> int:
    """
    Calculate the current streak for a habit.

    A streak is the number of consecutive periods where the goal was met
    (total completions >= goal_count). Includes the current period if goal is met.

    Args:
        habit_id: The ID of the habit
        goal_type: The period type ('daily', 'weekly', 'monthly')
        goal_count: The target count per period

    Returns:
        int: Streak count (0 if no streak)

    Algorithm:
        1. Start from the current period (include if goal is met)
        2. For each period going backward:
            a. Get completions in that period
            b. If total >= goal_count: increment streak, continue to previous period
            c. Else: break (streak ended)
        3. Return streak count

    Edge Cases:
        - No completions: Returns 0
        - Habit just created: Returns 0 (no complete periods)
        - Very long streaks: Safety limit of 3650 iterations (10 years daily)

    Example:
        Daily habit with goal 3/day:
        - Today: 3/3 ✓ (included in streak)
        - Yesterday: 3/3 ✓
        - 2 days ago: 3/3 ✓
        - 3 days ago: 1/3 ✗ (breaks streak)
        Result: Streak = 3
    """
    try:
        streak = 0
        today = get_today()

        # Start from the current period (include current period)
        period_date = today

        # Safety limit to prevent infinite loops
        # Daily: 3650 days (~10 years), Weekly: 520 weeks (~10 years), Monthly: 120 months (~10 years)
        max_iterations = 3650 if goal_type == "daily" else (520 if goal_type == "weekly" else 120)
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            # Get period boundaries for this period
            start_date, end_date = get_period_boundaries(goal_type, period_date)

            # Get all completions for this period
            completions = get_completions_for_habit(habit_id, start_date, end_date)
            total_count = sum(c.count for c in completions)

            # Check if goal was met in this period
            if total_count >= goal_count:
                streak += 1
                # Move to the previous period
                period_date = get_previous_period_start(period_date, goal_type)
            else:
                # Streak broken - stop counting
                break

        Logger.debug(
            f"StreakCalculator: Habit {habit_id} has streak of {streak} {goal_type} period(s)"
        )
        return streak

    except Exception as e:
        Logger.error(f"StreakCalculator: Error calculating streak for habit {habit_id}: {e}")
        return 0  # Safe default on error


def get_previous_period_start(
    reference_date: date,
    goal_type: Literal["daily", "weekly", "monthly"]
) -> date:
    """
    Get the start date of the period before the reference date's period.

    Args:
        reference_date: The reference date
        goal_type: The period type ('daily', 'weekly', 'monthly')

    Returns:
        date: Start date of the previous period

    Examples:
        Daily:
            reference_date = 2024-12-13 (Friday)
            -> returns 2024-12-12 (Thursday, previous day)

        Weekly:
            reference_date = 2024-12-13 (Friday in week Dec 9-15)
            -> returns 2024-12-02 (Monday of previous week)

        Monthly:
            reference_date = 2024-12-13 (December)
            -> returns 2024-11-01 (November 1st)

    Raises:
        ValueError: If goal_type is not 'daily', 'weekly', or 'monthly'
    """
    if goal_type == "daily":
        # Previous day
        return reference_date - timedelta(days=1)

    elif goal_type == "weekly":
        # Get Monday of current week (weekday 0 = Monday)
        current_week_monday = reference_date - timedelta(days=reference_date.weekday())
        # Go back 7 days to get Monday of previous week
        return current_week_monday - timedelta(days=7)

    elif goal_type == "monthly":
        # Get first day of current month
        current_month_start = reference_date.replace(day=1)
        # Go back one month to get first day of previous month
        return current_month_start - relativedelta(months=1)

    else:
        raise ValueError(
            f"Invalid goal_type '{goal_type}'. Must be 'daily', 'weekly', or 'monthly'."
        )
