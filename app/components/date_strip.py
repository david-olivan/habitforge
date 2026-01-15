"""
Date Navigation Strip Component for HabitForge

A horizontal 5-day date navigation strip that allows users to select
a specific date to view/log completions. Shows current day in center,
with 2 days before and 2 days after.
"""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.properties import ObjectProperty, StringProperty
from kivy.metrics import dp
from datetime import date, timedelta
from config.constants import BRAND_PRIMARY_RGB, hex_to_rgba
from logic.localization import _


# ============================================
# MONTH TRANSLATION MAPPING
# ============================================

# Mapping month numbers (1-12) to translation keys
MONTH_KEYS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
]


# ============================================
# DATE STRIP STYLING CONSTANTS
# ============================================

# Day button card dimensions
DAY_BUTTON_WIDTH = 58
DAY_BUTTON_HEIGHT = 56
DAY_BUTTON_RADIUS = 8
DAY_BUTTON_ELEVATION = 0.3

# Strip container
STRIP_SPACING = 6
STRIP_PADDING_HORIZONTAL = 12
STRIP_PADDING_VERTICAL = 8
STRIP_HEIGHT = 72

# Colors
COLOR_SELECTED_BG = BRAND_PRIMARY_RGB  # Orange for selected day
COLOR_UNSELECTED_BG = (1, 1, 1, 1)  # White for other days
COLOR_FUTURE_BG = (0.95, 0.95, 0.95, 1)  # Light grey for future days
COLOR_SELECTED_TEXT = (1, 1, 1, 1)  # White text for selected
COLOR_UNSELECTED_TEXT = (0.3, 0.3, 0.3, 1)  # Dark grey for unselected
COLOR_FUTURE_TEXT = (0.6, 0.6, 0.6, 1)  # Lighter grey text for future
COLOR_MONTH_TEXT = (0.5, 0.5, 0.5, 1)  # Medium grey for month abbreviation

# Typography
DAY_NUMBER_FONT_SIZE = "24sp"  # Large number
MONTH_ABBR_FONT_SIZE = "10sp"  # Small month abbreviation


class DayButton(MDCard):
    """
    A button representing a single day in the date strip.

    Shows:
    - Day number (large, e.g., "21")
    - Month abbreviation (small, e.g., "Dec")

    Visual state:
    - Selected: Orange background, white text
    - Unselected: White background, grey text
    """

    day_date = ObjectProperty(None)  # date object for this button
    is_selected = ObjectProperty(False)  # Whether this day is selected
    is_future = ObjectProperty(False)  # Whether this day is in the future
    on_click = ObjectProperty(None)  # Callback when button is tapped

    def __init__(self, day_date: date, is_selected: bool = False, is_future: bool = False, **kwargs):
        super().__init__(**kwargs)

        self.day_date = day_date
        self.is_selected = is_selected
        self.is_future = is_future

        # Card styling
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.width = dp(DAY_BUTTON_WIDTH)
        self.height = dp(DAY_BUTTON_HEIGHT)
        self.radius = dp(DAY_BUTTON_RADIUS)
        self.elevation = DAY_BUTTON_ELEVATION
        self.ripple_behavior = True  # Enable ripple effect on tap

        # Apply background color based on selection
        self._update_background_color()

        # Build UI
        self._build_ui()

        # Bind on_release to trigger callback
        self.bind(on_release=self._on_tap)

    def _get_translated_month_abbr(self, month_num: int) -> str:
        """Get 3-letter translated month abbreviation."""
        if 1 <= month_num <= 12:
            full_month = _(f"analytics.months.{MONTH_KEYS[month_num - 1]}")
            return full_month[:3]  # First 3 characters
        return ""

    def _build_ui(self):
        """Build button UI with day number and month abbreviation."""
        # Container for labels (vertically stacked)
        container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(0),
            padding=dp(4)
        )

        # Day number label (large)
        if self.is_selected:
            text_color = COLOR_SELECTED_TEXT
        elif self.is_future:
            text_color = COLOR_FUTURE_TEXT
        else:
            text_color = COLOR_UNSELECTED_TEXT

        self.day_number_label = MDLabel(
            text=str(self.day_date.day),
            halign="center",
            valign="bottom",
            theme_text_color="Custom",
            text_color=text_color,
            font_style="H5",
            font_size=DAY_NUMBER_FONT_SIZE,
            bold=True
        )
        container.add_widget(self.day_number_label)

        # Month abbreviation label (small)
        if self.is_selected:
            month_color = COLOR_SELECTED_TEXT
        elif self.is_future:
            month_color = COLOR_FUTURE_TEXT
        else:
            month_color = COLOR_MONTH_TEXT
        self.month_label = MDLabel(
            text=self._get_translated_month_abbr(self.day_date.month),  # Localized 3-letter month
            halign="center",
            valign="top",
            theme_text_color="Custom",
            text_color=month_color,
            font_style="Caption",
            font_size=MONTH_ABBR_FONT_SIZE
        )
        container.add_widget(self.month_label)

        self.add_widget(container)

    def _update_background_color(self):
        """Update card background color based on selection state."""
        if self.is_selected:
            self.md_bg_color = COLOR_SELECTED_BG
        elif self.is_future:
            self.md_bg_color = COLOR_FUTURE_BG  # Light grey for future
        else:
            self.md_bg_color = COLOR_UNSELECTED_BG  # White for past/today

    def _on_tap(self, instance):
        """Handle button tap."""
        if self.on_click:
            self.on_click(self.day_date)

    def set_selected(self, selected: bool):
        """Update selection state and refresh UI."""
        self.is_selected = selected
        self._update_background_color()

        # Update text colors
        if selected:
            text_color = COLOR_SELECTED_TEXT
            month_color = COLOR_SELECTED_TEXT
        elif self.is_future:
            text_color = COLOR_FUTURE_TEXT
            month_color = COLOR_FUTURE_TEXT
        else:
            text_color = COLOR_UNSELECTED_TEXT
            month_color = COLOR_MONTH_TEXT

        if hasattr(self, 'day_number_label'):
            self.day_number_label.text_color = text_color
        if hasattr(self, 'month_label'):
            self.month_label.text_color = month_color


class DateNavigationStrip(MDBoxLayout):
    """
    Horizontal 5-day date navigation strip.

    Shows:
    - Current day (center)
    - 2 days before
    - 2 days after

    User can tap any day to select it. Selected day is highlighted
    with orange background.

    Properties:
        selected_date: The currently selected date
        on_date_changed: Callback when user selects a different date
    """

    today_date = ObjectProperty(date.today())  # Today's actual date (always center)
    selected_date = ObjectProperty(date.today())  # Current selected date (can differ from today)
    on_date_changed = ObjectProperty(None)  # Callback(new_date)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Strip container styling
        self.orientation = "horizontal"
        self.spacing = dp(STRIP_SPACING)
        self.padding = (dp(STRIP_PADDING_HORIZONTAL), dp(STRIP_PADDING_VERTICAL))
        self.size_hint_y = None
        self.height = dp(STRIP_HEIGHT)

        # Track day buttons
        self.day_buttons = []  # List of DayButton widgets

        # Build initial UI
        self.refresh_strip()

    def refresh_strip(self):
        """Rebuild the 5-day strip centered on today_date."""
        # Clear existing buttons
        self.clear_widgets()
        self.day_buttons = []

        # Calculate 5-day range: always center on TODAY, not selected date
        dates = [
            self.today_date - timedelta(days=2),
            self.today_date - timedelta(days=1),
            self.today_date,
            self.today_date + timedelta(days=1),
            self.today_date + timedelta(days=2)
        ]

        # Create button for each date
        for day_date in dates:
            is_selected = (day_date == self.selected_date)
            is_future = (day_date > self.today_date)
            button = DayButton(
                day_date=day_date,
                is_selected=is_selected,
                is_future=is_future
            )
            button.on_click = self._on_day_selected

            self.add_widget(button)
            self.day_buttons.append(button)

    def _on_day_selected(self, new_date: date):
        """Handle when user taps a day button."""
        # Don't do anything if same date
        if new_date == self.selected_date:
            return

        # Update selected date
        old_selected = self.selected_date
        self.selected_date = new_date

        # Update button states WITHOUT rebuilding the strip
        for button in self.day_buttons:
            if button.day_date == old_selected:
                button.set_selected(False)  # Deselect old
            if button.day_date == new_date:
                button.set_selected(True)   # Select new

        # Fire callback to parent
        if self.on_date_changed:
            self.on_date_changed(new_date)

    def set_selected_date(self, new_date: date):
        """
        Programmatically change selected date (without firing callback).

        Use this when you want to update the strip from external code
        without triggering the on_date_changed callback.
        """
        self.selected_date = new_date
        self.refresh_strip()