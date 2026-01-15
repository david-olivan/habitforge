"""
Data Models for HabitForge

This module defines the data models for habit tracking with built-in validation.
Uses simple Python classes with manual validation (no external dependencies).
"""

import re
from datetime import datetime
from datetime import date as DateType
from typing import Literal, Optional, Dict, Any


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


def validate_name(name: str) -> str:
    """
    Validate and sanitize habit name.

    Args:
        name: The habit name to validate

    Returns:
        str: Sanitized habit name

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(name, str):
        raise ValidationError("name must be a string")

    name = name.strip()

    if not name:
        raise ValidationError("Habit name cannot be empty or whitespace only")

    if len(name) > 50:
        raise ValidationError("Habit name must be 50 characters or less")

    return name


def validate_color(color: str) -> str:
    """
    Validate hex color code.

    Args:
        color: Hex color code to validate

    Returns:
        str: Validated color code

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(color, str):
        raise ValidationError("color must be a string")

    if not re.match(r"^#[0-9A-Fa-f]{6}$", color):
        raise ValidationError("color must be a valid hex color code (#RRGGBB)")

    return color


def validate_goal_type(goal_type: str) -> str:
    """
    Validate goal type.

    Args:
        goal_type: Goal type to validate

    Returns:
        str: Validated goal type

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(goal_type, str):
        raise ValidationError("goal_type must be a string")

    valid_types = ["daily", "weekly", "monthly"]
    if goal_type not in valid_types:
        raise ValidationError(f"goal_type must be one of: {', '.join(valid_types)}")

    return goal_type


def validate_goal_count(goal_count: int) -> int:
    """
    Validate goal count.

    Args:
        goal_count: Goal count to validate

    Returns:
        int: Validated goal count

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(goal_count, int):
        raise ValidationError("goal_count must be an integer")

    if goal_count < 1 or goal_count > 100:
        raise ValidationError("goal_count must be between 1 and 100")

    return goal_count


def validate_date(date: DateType) -> DateType:
    """
    Validate that date is not in the future.

    Args:
        date: Date to validate

    Returns:
        date: Validated date

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(date, DateType):
        raise ValidationError("date must be a date object")

    today = DateType.today()
    if date > today:
        raise ValidationError("Completion date cannot be in the future")

    return date


class HabitBase:
    """
    Base habit model with common fields and validation.

    This model contains all the fields that users provide when creating/editing habits.
    """

    def __init__(self, name: str, color: str, goal_type: str, goal_count: int):
        """
        Initialize habit with validation.

        Args:
            name: Habit name (1-50 characters)
            color: Hex color code (#RRGGBB)
            goal_type: Goal frequency (daily, weekly, or monthly)
            goal_count: Target count per period (1-100)

        Raises:
            ValidationError: If any field is invalid
        """
        self.name = validate_name(name)
        self.color = validate_color(color)
        self.goal_type = validate_goal_type(goal_type)
        self.goal_count = validate_goal_count(goal_count)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding None values)"""
        return {
            "name": self.name,
            "color": self.color,
            "goal_type": self.goal_type,
            "goal_count": self.goal_count,
        }


class HabitCreate(HabitBase):
    """
    Model for creating a new habit.

    Inherits all fields from HabitBase. No additional fields needed.
    Used to validate data before inserting into database.
    """
    pass


class HabitUpdate:
    """
    Model for updating an existing habit.

    All fields are optional to allow partial updates.
    Only provided fields will be validated and updated.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        color: Optional[str] = None,
        goal_type: Optional[str] = None,
        goal_count: Optional[int] = None,
        archived: Optional[bool] = None,
    ):
        """
        Initialize update model with optional fields.

        Args:
            name: Optional habit name
            color: Optional hex color code
            goal_type: Optional goal frequency
            goal_count: Optional target count
            archived: Optional archive status

        Raises:
            ValidationError: If any provided field is invalid
        """
        self.name = validate_name(name) if name is not None else None
        self.color = validate_color(color) if color is not None else None
        self.goal_type = validate_goal_type(goal_type) if goal_type is not None else None
        self.goal_count = validate_goal_count(goal_count) if goal_count is not None else None
        self.archived = archived

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding None values)"""
        data = {}
        if self.name is not None:
            data["name"] = self.name
        if self.color is not None:
            data["color"] = self.color
        if self.goal_type is not None:
            data["goal_type"] = self.goal_type
        if self.goal_count is not None:
            data["goal_count"] = self.goal_count
        if self.archived is not None:
            data["archived"] = self.archived
        return data


class Habit(HabitBase):
    """
    Complete habit model with database fields.

    Represents a habit as stored in the database.
    Includes auto-generated fields (id, created_at) and archive status.
    """

    def __init__(
        self,
        name: str,
        color: str,
        goal_type: str,
        goal_count: int,
        id: int,
        created_at: datetime,
        archived: bool = False,
    ):
        """
        Initialize complete habit model.

        Args:
            name: Habit name
            color: Hex color code
            goal_type: Goal frequency
            goal_count: Target count per period
            id: Database ID
            created_at: Creation timestamp
            archived: Archive status
        """
        super().__init__(name, color, goal_type, goal_count)
        self.id = id
        self.created_at = created_at
        self.archived = archived

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = super().to_dict()
        data.update({
            "id": self.id,
            "created_at": self.created_at,
            "archived": self.archived,
        })
        return data

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "Habit":
        """
        Create a Habit instance from a database row.

        Args:
            row: Dictionary containing habit data from database

        Returns:
            Habit: Validated Habit instance

        Raises:
            ValidationError: If database row has invalid data
        """
        return cls(
            id=row["id"],
            name=row["name"],
            color=row["color"],
            goal_type=row["goal_type"],
            goal_count=row["goal_count"],
            created_at=row["created_at"],
            archived=bool(row.get("archived", 0)),
        )


class CompletionBase:
    """
    Base completion model with common fields and validation.

    This model represents a habit completion record with the date and count.
    """

    def __init__(self, habit_id: int, date: DateType, count: int = 1):
        """
        Initialize completion with validation.

        Args:
            habit_id: ID of the associated habit
            date: Date of the completion
            count: Number of completions (0 or more)

        Raises:
            ValidationError: If any field is invalid
        """
        if not isinstance(habit_id, int) or habit_id <= 0:
            raise ValidationError("habit_id must be a positive integer")

        if not isinstance(count, int) or count < 0:
            raise ValidationError("count must be a non-negative integer")

        self.habit_id = habit_id
        self.date = validate_date(date)
        self.count = count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "habit_id": self.habit_id,
            "date": self.date,
            "count": self.count,
        }


class CompletionCreate(CompletionBase):
    """
    Model for creating a new completion.

    Inherits all fields from CompletionBase. Used to validate data
    before inserting into database.
    """
    pass


class Completion(CompletionBase):
    """
    Complete completion model with database fields.

    Represents a completion as stored in the database.
    Includes auto-generated fields (id, completed_at).
    """

    def __init__(
        self,
        habit_id: int,
        date: DateType,
        count: int,
        id: int,
        completed_at: datetime,
    ):
        """
        Initialize complete completion model.

        Args:
            habit_id: ID of the associated habit
            date: Date of the completion
            count: Number of completions
            id: Database ID
            completed_at: Completion timestamp
        """
        super().__init__(habit_id, date, count)
        self.id = id
        self.completed_at = completed_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = super().to_dict()
        data.update({
            "id": self.id,
            "completed_at": self.completed_at,
        })
        return data

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "Completion":
        """
        Create a Completion instance from a database row.

        Args:
            row: Dictionary containing completion data from database

        Returns:
            Completion: Validated Completion instance

        Raises:
            ValidationError: If database row has invalid data
        """
        # Convert date string from database to date object
        date_value = row["date"]
        if isinstance(date_value, str):
            date_value = datetime.strptime(date_value, "%Y-%m-%d").date()

        return cls(
            id=row["id"],
            habit_id=row["habit_id"],
            date=date_value,
            count=row["count"],
            completed_at=row["completed_at"],
        )
