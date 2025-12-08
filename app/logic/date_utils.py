"""
Date Utilities for HabitForge

This module provides date calculation utilities for different habit periods
(daily, weekly, monthly).
"""

from datetime import date, timedelta
from typing import Tuple, Literal
from dateutil.relativedelta import relativedelta


def get_today() -> date:
    """
    Get today's date.

    Wrapper function for testing purposes.

    Returns:
        date: Current date
    """
    return date.today()


def get_period_boundaries(
    goal_type: Literal["daily", "weekly", "monthly"], reference_date: date = None
) -> Tuple[date, date]:
    """
    Calculate the start and end dates for a period based on goal type.

    Period definitions:
    - Daily: Same day (reference_date, reference_date)
    - Weekly: Monday to Sunday of the reference date's week
    - Monthly: 1st to last day of the reference date's month

    Args:
        goal_type: The type of goal period ('daily', 'weekly', 'monthly')
        reference_date: The date to calculate period for (defaults to today)

    Returns:
        Tuple[date, date]: (start_date, end_date) inclusive

    Raises:
        ValueError: If goal_type is not valid
    """
    if reference_date is None:
        reference_date = get_today()

    if goal_type == "daily":
        # Daily period is just the single day
        return (reference_date, reference_date)

    elif goal_type == "weekly":
        # Week runs Monday (0) to Sunday (6)
        # Find Monday of the week
        days_since_monday = reference_date.weekday()  # 0=Monday, 6=Sunday
        start_date = reference_date - timedelta(days=days_since_monday)
        end_date = start_date + timedelta(days=6)  # Sunday
        return (start_date, end_date)

    elif goal_type == "monthly":
        # Month runs from 1st to last day
        start_date = reference_date.replace(day=1)
        # Get last day of month by going to 1st of next month, then back one day
        next_month = start_date + relativedelta(months=1)
        end_date = next_month - timedelta(days=1)
        return (start_date, end_date)

    else:
        raise ValueError(
            f"Invalid goal_type '{goal_type}'. Must be 'daily', 'weekly', or 'monthly'."
        )


def is_date_in_current_period(
    date_to_check: date, goal_type: Literal["daily", "weekly", "monthly"]
) -> bool:
    """
    Check if a date falls within the current period for a goal type.

    Args:
        date_to_check: The date to check
        goal_type: The type of goal period

    Returns:
        bool: True if date is in current period, False otherwise
    """
    start_date, end_date = get_period_boundaries(goal_type, reference_date=get_today())
    return start_date <= date_to_check <= end_date


def get_days_in_period(goal_type: Literal["daily", "weekly", "monthly"]) -> int:
    """
    Get the number of days in a period for a goal type.

    Args:
        goal_type: The type of goal period

    Returns:
        int: Number of days in the period
    """
    if goal_type == "daily":
        return 1
    elif goal_type == "weekly":
        return 7
    elif goal_type == "monthly":
        # Calculate for current month
        today = get_today()
        start_date, end_date = get_period_boundaries("monthly", today)
        return (end_date - start_date).days + 1
    else:
        raise ValueError(
            f"Invalid goal_type '{goal_type}'. Must be 'daily', 'weekly', or 'monthly'."
        )


def format_period_label(
    goal_type: Literal["daily", "weekly", "monthly"], reference_date: date = None
) -> str:
    """
    Generate a human-readable label for a period.

    Examples:
    - Daily: "Today (Mon, Dec 8)"
    - Weekly: "Week of Dec 4-10"
    - Monthly: "December 2024"

    Args:
        goal_type: The type of goal period
        reference_date: The date to format (defaults to today)

    Returns:
        str: Formatted period label
    """
    if reference_date is None:
        reference_date = get_today()

    if goal_type == "daily":
        return reference_date.strftime("%A, %b %d")

    elif goal_type == "weekly":
        start_date, end_date = get_period_boundaries("weekly", reference_date)
        return f"Week of {start_date.strftime('%b %d')} - {end_date.strftime('%b %d')}"

    elif goal_type == "monthly":
        return reference_date.strftime("%B %Y")

    else:
        raise ValueError(
            f"Invalid goal_type '{goal_type}'. Must be 'daily', 'weekly', or 'monthly'."
        )
