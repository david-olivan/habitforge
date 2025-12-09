"""
Application Constants for HabitForge

This module contains all app-wide constants including color palettes,
validation limits, and configuration values.
"""

# ============================================
# BRAND COLOR PALETTE
# ============================================
# Brand colors extracted from app logo (habitforge-icon-flat.svg, habitforge-icon.svg)
# Used for app UI elements like top bar, navigation, buttons

# Primary brand color (orange from logo)
BRAND_PRIMARY = "#FF6B35"  # Vibrant orange
BRAND_PRIMARY_RGB = (1.0, 0.42, 0.21, 1)  # Kivy RGB format

# Flame gradient colors (from detailed icon)
BRAND_FLAME_MID = "#FFB84D"  # Mid-flame yellow-orange
BRAND_FLAME_BRIGHT = "#FFF4A3"  # Bright flame yellow

# Grayscale colors from anvil (for secondary UI elements)
BRAND_DARK_1 = "#2A2A2A"  # Darkest
BRAND_DARK_2 = "#3D3D3D"
BRAND_GRAY_1 = "#505050"
BRAND_GRAY_2 = "#5A5A5A"
BRAND_GRAY_3 = "#6B6B6B"
BRAND_GRAY_4 = "#7A7A7A"  # Lightest gray

# Helper function to convert hex to Kivy RGBA tuple
def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> tuple:
    """
    Convert hex color to Kivy RGBA tuple format.

    Args:
        hex_color: Hex color string (e.g., "#FF6B35")
        alpha: Alpha/opacity value (0.0 to 1.0)

    Returns:
        Tuple of (r, g, b, a) with values from 0.0 to 1.0
    """
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b, alpha)


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