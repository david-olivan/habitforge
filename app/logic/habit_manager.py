"""
Habit Business Logic for HabitForge

This module contains business rules and validation logic for habits.
Field validation is handled by the schemas module, and this module
adds database-level validation (e.g., unique name checks).
"""

from typing import Tuple, Dict
from models.database import get_all_habits
from models.schemas import HabitCreate, HabitUpdate, ValidationError
from kivy.logger import Logger


def check_unique_name(name: str, exclude_id: int | None = None) -> bool:
    """
    Check if a habit name is unique (case-insensitive).

    Args:
        name: Habit name to check
        exclude_id: Habit ID to exclude from check (for edit operations)

    Returns:
        bool: True if name is unique, False if duplicate exists
    """
    try:
        # Get all habits (including archived to check against all names)
        habits = get_all_habits(include_archived=True)

        # Normalize name for comparison (case-insensitive, trimmed)
        normalized_name = name.strip().lower()

        for habit in habits:
            # Skip the habit being edited
            if exclude_id is not None and habit.id == exclude_id:
                continue

            # Check for duplicate name
            if habit.name.strip().lower() == normalized_name:
                Logger.info(
                    f"HabitManager: Duplicate name found: '{name}' matches habit ID {habit.id}"
                )
                return False

        Logger.info(f"HabitManager: Name '{name}' is unique")
        return True
    except Exception as e:
        Logger.error(f"HabitManager: Error checking unique name: {e}")
        # On error, assume not unique to be safe
        return False


def validate_habit_for_save(
    habit_data: dict, habit_id: int | None = None
) -> Tuple[bool, Dict[str, str]]:
    """
    Validate habit data before saving to database.

    Combines Pydantic validation with business logic validation.

    Args:
        habit_data: Dictionary with habit fields (name, color, goal_type, goal_count)
        habit_id: ID of habit being edited (None for new habit)

    Returns:
        Tuple[bool, Dict[str, str]]: (is_valid, error_dict)
        - is_valid: True if all validations pass
        - error_dict: Maps field names to error messages (empty if valid)
    """
    errors = {}

    # Step 1: Validate with schemas
    try:
        if habit_id is None:
            # Creating new habit - validate all required fields
            HabitCreate(**habit_data)
        else:
            # Updating existing habit - validate provided fields
            HabitUpdate(**habit_data)

        Logger.info(f"HabitManager: Schema validation passed for habit data")
    except ValidationError as e:
        # ValidationError message format is simple: "error message"
        error_msg = str(e)

        # Try to extract field name from common error patterns
        if "name" in error_msg.lower():
            errors["name"] = error_msg
        elif "color" in error_msg.lower():
            errors["color"] = error_msg
        elif "goal_type" in error_msg.lower():
            errors["goal_type"] = error_msg
        elif "goal_count" in error_msg.lower():
            errors["goal_count"] = error_msg
        else:
            # Generic error - assign to first field that had data
            if "name" in habit_data:
                errors["name"] = error_msg
            else:
                errors["general"] = error_msg

        Logger.warning(
            f"HabitManager: Schema validation failed with {len(errors)} error(s)"
        )

    # Step 2: Check unique name constraint (database-level validation)
    if "name" in habit_data and "name" not in errors:
        name = habit_data["name"]
        if not check_unique_name(name, exclude_id=habit_id):
            errors["name"] = "A habit with this name already exists"
            Logger.warning(f"HabitManager: Unique name check failed for '{name}'")

    # Step 3: Return results
    is_valid = len(errors) == 0

    if is_valid:
        Logger.info(f"HabitManager: Habit data is valid")
    else:
        Logger.warning(f"HabitManager: Validation failed with errors: {errors}")

    return (is_valid, errors)