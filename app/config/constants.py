"""
Application Constants for HabitForge

This module contains all app-wide constants including color palettes,
validation limits, and configuration values.
"""

# ============================================
# COLOR PALETTE FOR HABITS
# ============================================
# Material Design inspired colors for habit visualization
# Users can choose from these predefined colors when creating habits

HABIT_COLORS = [
    "#E57373",  # Red - High energy, urgent habits
    "#FFB74D",  # Orange - Warm, creative habits
    "#FFF176",  # Yellow - Bright, positive habits
    "#81C784",  # Green - Health, growth habits
    "#4DB6AC",  # Teal - Calm, productive habits
    "#64B5F6",  # Blue - Focus, learning habits
    "#BA68C8",  # Purple - Spiritual, mindful habits
    "#F06292",  # Pink - Social, relationship habits
]

# Default color for new habits
DEFAULT_HABIT_COLOR = HABIT_COLORS[0]  # Red


# ============================================
# VALIDATION CONSTANTS
# ============================================
# These match the Pydantic model constraints

MAX_HABIT_NAME_LENGTH = 50
MIN_HABIT_NAME_LENGTH = 1

MAX_GOAL_COUNT = 100
MIN_GOAL_COUNT = 1


# ============================================
# GOAL TYPES
# ============================================
# Valid goal frequency types

GOAL_TYPES = ["daily", "weekly", "monthly"]

# User-friendly labels for goal types
GOAL_TYPE_LABELS = {
    "daily": "Daily",
    "weekly": "Weekly",
    "monthly": "Monthly",
}

# Default goal type for new habits
DEFAULT_GOAL_TYPE = "daily"

# Default goal count for new habits
DEFAULT_GOAL_COUNT = 1


# ============================================
# UI CONSTANTS
# ============================================

# Color picker grid dimensions
COLOR_PICKER_COLUMNS = 4
COLOR_PICKER_ROWS = 2

# Form field spacing
FORM_FIELD_SPACING = "12dp"
FORM_SECTION_SPACING = "24dp"

# Button sizes
BUTTON_HEIGHT = "48dp"
FAB_SIZE = "56dp"


# ============================================
# DATABASE CONSTANTS
# ============================================

DATABASE_NAME = "habitforge.db"
DATABASE_VERSION = 1


# ============================================
# APP METADATA
# ============================================

APP_NAME = "HabitForge"
APP_VERSION = "0.1.0"
APP_AUTHOR = "Davs"