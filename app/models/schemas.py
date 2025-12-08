"""
Pydantic Data Models for HabitForge

This module defines the data models for habit tracking with built-in validation.
Uses Pydantic v2 for automatic field validation and type checking.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal


class HabitBase(BaseModel):
    """
    Base habit model with common fields and validation.

    This model contains all the fields that users provide when creating/editing habits.
    Validation rules are enforced automatically by Pydantic.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Habit name (1-50 characters)",
    )
    color: str = Field(
        ..., pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code (#RRGGBB)"
    )
    goal_type: Literal["daily", "weekly", "monthly"] = Field(
        ..., description="Goal frequency (daily, weekly, or monthly)"
    )
    goal_count: int = Field(
        ..., ge=1, le=100, description="Target count per period (1-100)"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validate and sanitize habit name.

        Strips leading/trailing whitespace and ensures the result is not empty.

        Args:
            v: The habit name to validate

        Returns:
            str: Sanitized habit name

        Raises:
            ValueError: If name is empty after stripping whitespace
        """
        v = v.strip()
        if not v:
            raise ValueError("Habit name cannot be empty or whitespace only")
        return v


class HabitCreate(HabitBase):
    """
    Model for creating a new habit.

    Inherits all fields from HabitBase. No additional fields needed.
    Used to validate data before inserting into database.
    """

    pass


class HabitUpdate(BaseModel):
    """
    Model for updating an existing habit.

    All fields are optional to allow partial updates.
    Only provided fields will be validated and updated.
    """

    name: str | None = Field(None, min_length=1, max_length=50)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    goal_type: Literal["daily", "weekly", "monthly"] | None = None
    goal_count: int | None = Field(None, ge=1, le=100)
    archived: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """
        Validate and sanitize habit name if provided.

        Args:
            v: The habit name to validate (can be None)

        Returns:
            str | None: Sanitized habit name or None

        Raises:
            ValueError: If name is empty after stripping whitespace
        """
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Habit name cannot be empty or whitespace only")
        return v


class Habit(HabitBase):
    """
    Complete habit model with database fields.

    Represents a habit as stored in the database.
    Includes auto-generated fields (id, created_at) and archive status.
    """

    id: int
    created_at: datetime
    archived: bool = False

    class Config:
        """Pydantic configuration"""

        from_attributes = True  # Allows .model_validate() from dict/object

    @classmethod
    def from_db_row(cls, row: dict) -> "Habit":
        """
        Create a Habit instance from a database row.

        Factory method to convert database query results into Habit objects.

        Args:
            row: Dictionary containing habit data from database

        Returns:
            Habit: Validated Habit instance

        Raises:
            ValidationError: If database row has invalid data
        """
        return cls.model_validate(row)