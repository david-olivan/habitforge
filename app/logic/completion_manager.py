"""
Completion Business Logic for HabitForge

This module contains business logic for managing habit completions,
calculating progress, and validating completion operations.
"""

from datetime import date
from typing import Tuple, Optional, Dict, List
from models.database import (
    get_habit_by_id,
    increment_completion,
    decrement_completion,
    get_completion_for_date,
    get_completions_for_habit,
)
from models.schemas import Completion
from logic.date_utils import get_today, get_period_boundaries
from logic.heatmap_data import HeatmapDataCache
from kivy.logger import Logger


def log_completion(
    habit_id: int, completion_date: Optional[date] = None, amount: int = 1
) -> Tuple[bool, Optional[str], Optional[Completion]]:
    """
    Log a completion for a habit on a specific date.

    This is the main entry point for recording habit completions.
    Validates the habit exists and the date is not in the future.

    Args:
        habit_id: The ID of the habit
        completion_date: The date of the completion (defaults to today)
        amount: Amount to increment by (default 1)

    Returns:
        Tuple[bool, Optional[str], Optional[Completion]]:
            - success: True if completion was logged successfully
            - error_message: Error description if failed, None if successful
            - completion: The Completion object if successful, None if failed
    """
    # Default to today if no date provided
    if completion_date is None:
        completion_date = get_today()

    # Validate date is not in future
    if completion_date > get_today():
        error_msg = "Cannot log completions for future dates"
        Logger.warning(f"CompletionManager: {error_msg}")
        return (False, error_msg, None)

    # Validate amount is positive
    if amount <= 0:
        error_msg = "Completion amount must be positive"
        Logger.warning(f"CompletionManager: {error_msg}")
        return (False, error_msg, None)

    # Validate habit exists
    habit = get_habit_by_id(habit_id)
    if not habit:
        error_msg = f"Habit with ID {habit_id} not found"
        Logger.warning(f"CompletionManager: {error_msg}")
        return (False, error_msg, None)

    # Check if habit is archived
    if habit.archived:
        error_msg = "Cannot log completions for archived habits"
        Logger.warning(f"CompletionManager: {error_msg}")
        return (False, error_msg, None)

    # Log the completion
    completion = increment_completion(habit_id, completion_date, amount)

    if completion:
        Logger.info(
            f"CompletionManager: Logged {amount} completion(s) for habit {habit_id}"
        )
        # Invalidate heatmap cache for this habit so analytics shows fresh data
        HeatmapDataCache.invalidate_habit(habit_id)
        return (True, None, completion)
    else:
        error_msg = "Failed to log completion in database"
        return (False, error_msg, None)


def undo_completion(
    habit_id: int, completion_date: Optional[date] = None, amount: int = 1
) -> Tuple[bool, Optional[str], Optional[Completion]]:
    """
    Undo (decrement) a completion for a habit on a specific date.

    Validates the habit exists and prevents negative counts.

    Args:
        habit_id: The ID of the habit
        completion_date: The date of the completion (defaults to today)
        amount: Amount to decrement by (default 1)

    Returns:
        Tuple[bool, Optional[str], Optional[Completion]]:
            - success: True if completion was decremented successfully
            - error_message: Error description if failed, None if successful
            - completion: The updated Completion object if successful, None if failed
    """
    # Default to today if no date provided
    if completion_date is None:
        completion_date = get_today()

    # Validate amount is positive
    if amount <= 0:
        error_msg = "Decrement amount must be positive"
        Logger.warning(f"CompletionManager: {error_msg}")
        return (False, error_msg, None)

    # Validate habit exists
    habit = get_habit_by_id(habit_id)
    if not habit:
        error_msg = f"Habit with ID {habit_id} not found"
        Logger.warning(f"CompletionManager: {error_msg}")
        return (False, error_msg, None)

    # Decrement the completion
    completion = decrement_completion(habit_id, completion_date, amount)

    if completion:
        Logger.info(
            f"CompletionManager: Decremented {amount} completion(s) for habit {habit_id}"
        )
        return (True, None, completion)
    else:
        error_msg = "No completion found to decrement"
        return (False, error_msg, None)


def get_habit_progress(
    habit_id: int,
    goal_count: int,
    goal_type: str,
    reference_date: Optional[date] = None,
) -> Dict:
    """
    Calculate progress toward a habit goal for a specific period.

    For daily goals: Uses the specific reference date (or today)
    For weekly/monthly goals: Sums all completions in the current period

    Args:
        habit_id: The ID of the habit
        goal_count: The target count for the period
        goal_type: 'daily', 'weekly', or 'monthly'
        reference_date: The date to calculate progress for (defaults to today)

    Returns:
        Dict with keys:
            - current_count: int (number of completions)
            - goal_count: int (target number)
            - percentage: float (0-100)
            - goal_met: bool
            - remaining: int (completions needed, 0 if goal met)
            - date: date (reference date used)
    """
    if reference_date is None:
        reference_date = get_today()

    # Get period boundaries based on goal type
    start_date, end_date = get_period_boundaries(goal_type, reference_date)

    # Get completions for the period
    completions = get_completions_for_habit(habit_id, start_date, end_date)

    # Sum up all completion counts in the period
    current_count = sum(c.count for c in completions)

    # Calculate progress metrics
    percentage = min(100.0, (current_count / goal_count * 100) if goal_count > 0 else 0)
    goal_met = current_count >= goal_count
    remaining = max(0, goal_count - current_count)

    progress = {
        "current_count": current_count,
        "goal_count": goal_count,
        "percentage": round(percentage, 1),
        "goal_met": goal_met,
        "remaining": remaining,
        "date": reference_date,
        "period_start": start_date,
        "period_end": end_date,
    }

    Logger.debug(
        f"CompletionManager: Progress for habit {habit_id}: {current_count}/{goal_count} ({percentage:.1f}%)"
    )

    return progress


def get_period_completions(
    habit_id: int, goal_type: str, reference_date: Optional[date] = None
) -> List[Completion]:
    """
    Get all completions for a habit in the current period.

    Args:
        habit_id: The ID of the habit
        goal_type: 'daily', 'weekly', or 'monthly'
        reference_date: The date to calculate period for (defaults to today)

    Returns:
        List[Completion]: List of completions in the period
    """
    if reference_date is None:
        reference_date = get_today()

    # Get period boundaries
    start_date, end_date = get_period_boundaries(goal_type, reference_date)

    # Query completions for the period
    completions = get_completions_for_habit(habit_id, start_date, end_date)

    Logger.debug(
        f"CompletionManager: Found {len(completions)} completion(s) for habit {habit_id} in period"
    )

    return completions


def get_completion_count_for_date(habit_id: int, completion_date: date) -> int:
    """
    Get the completion count for a habit on a specific date.

    Args:
        habit_id: The ID of the habit
        completion_date: The date to query

    Returns:
        int: Completion count (0 if no completions logged)
    """
    completion = get_completion_for_date(habit_id, completion_date)
    return completion.count if completion else 0


def validate_completion_data(
    habit_id: int, completion_date: date, amount: int = 1
) -> Tuple[bool, Optional[str]]:
    """
    Validate completion data before logging.

    Args:
        habit_id: The ID of the habit
        completion_date: The date of the completion
        amount: The amount to log

    Returns:
        Tuple[bool, Optional[str]]:
            - is_valid: True if validation passed
            - error_message: Error description if failed, None if valid
    """
    # Check habit exists
    habit = get_habit_by_id(habit_id)
    if not habit:
        return (False, f"Habit with ID {habit_id} not found")

    # Check habit is not archived
    if habit.archived:
        return (False, "Cannot log completions for archived habits")

    # Check date is not in future
    if completion_date > get_today():
        return (False, "Cannot log completions for future dates")

    # Check amount is positive
    if amount <= 0:
        return (False, "Completion amount must be positive")

    return (True, None)
