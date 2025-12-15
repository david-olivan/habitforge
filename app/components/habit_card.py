"""
Habit Card Component for HabitForge

A reusable card widget that displays a habit with its progress,
goal information, and an increment button.
"""

from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDIcon
from kivymd.icon_definitions import md_icons
from kivy.properties import DictProperty, ObjectProperty, NumericProperty
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from config.constants import GOAL_TYPE_LABELS, BRAND_PRIMARY_RGB, BRAND_FLAME_MID, hex_to_rgba

# ============================================
# HABIT CARD STYLING CONSTANTS
# ============================================

# Card dimensions and styling
CARD_HEIGHT = 64
CARD_RADIUS = 8
CARD_ELEVATION = 0.5
CARD_PADDING_MAIN = 12
CARD_SPACING_MAIN = 8

# Colors
COLOR_WHITE = (1, 1, 1, 1)
COLOR_LIGHT_GREY = (0.95, 0.95, 0.95, 1)
COLOR_DARK_GREY = (0.5, 0.5, 0.5, 1)
COLOR_FALLBACK_RED = (0.9, 0.3, 0.3, 1)

# Habit name label
HABIT_NAME_WIDTH = 120
HABIT_NAME_PADDING_HORIZONTAL = 8
HABIT_NAME_PADDING_VERTICAL = 4
HABIT_NAME_RADIUS = 8

# Streak display
STREAK_CONTAINER_WIDTH = 40
STREAK_SPACING = 2
STREAK_PADDING_LEFT = 4
STREAK_LABEL_WIDTH = 12
STREAK_ICON_SIZE = 20

# Completion button
BUTTON_TOUCH_AREA = 30
BUTTON_BACKGROUND_SIZE = 30  # Visual background size (can be smaller than touch area)
BUTTON_BACKGROUND_RADIUS = 6
BUTTON_ICON_SIZE = "20sp"


class HabitCard(MDCard):
    """
    A card widget displaying habit information and progress.

    Shows (single horizontal row):
    - Habit name with colored background (strikethrough when goal met)
    - Streak indicator (flame icon with count)
    - Progress (current/goal count)
    - Increment button (larger, 56dp)

    Card background darkens when goal is met.
    """

    # Properties
    habit = DictProperty({})  # Habit data (id, name, color, goal_type, goal_count)
    progress = DictProperty(
        {}
    )  # Progress data (current_count, goal_count, percentage, goal_met)
    on_increment = ObjectProperty(
        None
    )  # Callback function when increment button pressed

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Card styling
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(CARD_HEIGHT)
        self.md_bg_color = COLOR_WHITE
        self.elevation = CARD_ELEVATION
        self.radius = [dp(CARD_RADIUS)]
        self.padding = dp(0)

        # Build the UI
        self.build_ui()

        # Update display with initial data if provided
        if self.habit:
            self.update_habit_display()
        if self.progress:
            self.update_progress_display()

    def build_ui(self):
        """Build the card UI layout - single horizontal row."""
        # Main container - horizontal row layout
        main_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(CARD_SPACING_MAIN),
            padding=[dp(CARD_PADDING_MAIN), dp(CARD_PADDING_MAIN), dp(CARD_PADDING_MAIN), dp(CARD_PADDING_MAIN)],
            pos_hint={"center_y": 0.5}  # Center vertically in card
        )

        # Habit name label with colored background
        self.name_label = MDLabel(
            text="Habit Name",
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=COLOR_WHITE,
            markup=True,  # Enable markup for strikethrough
            shorten=True,  # Enable text truncation
            shorten_from="right",  # Truncate from right with ellipsis
            size_hint_x=None,
            width=dp(HABIT_NAME_WIDTH),
            padding=[dp(HABIT_NAME_PADDING_HORIZONTAL), dp(HABIT_NAME_PADDING_VERTICAL),
                     dp(HABIT_NAME_PADDING_HORIZONTAL), dp(HABIT_NAME_PADDING_VERTICAL)],
            pos_hint={"center_y": 0.5}  # Center vertically
        )

        # Add colored rounded rectangle background to habit name
        with self.name_label.canvas.before:
            self.name_bg_color = Color(rgba=COLOR_FALLBACK_RED)
            self.name_bg_rect = RoundedRectangle(
                pos=self.name_label.pos,
                size=self.name_label.size,
                radius=[dp(HABIT_NAME_RADIUS)]
            )
        self.name_label.bind(
            pos=self._update_name_bg_rect,
            size=self._update_name_bg_rect
        )

        # Streak container - groups number and icon tightly together
        self.streak_container = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            width=dp(STREAK_CONTAINER_WIDTH),
            spacing=dp(STREAK_SPACING),
            padding=[dp(STREAK_PADDING_LEFT), 0, 0, 0],
            pos_hint={"center_y": 0.5}  # Center vertically
        )

        # Streak count label (number before icon)
        self.streak_label = MDLabel(
            text="0",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLOR_DARK_GREY,
            size_hint_x=None,
            width=dp(STREAK_LABEL_WIDTH),
            halign="right",
        )

        # Streak icon (flame) - using Material Design Icons
        self.streak_icon = MDIcon(
            icon="fire",
            theme_text_color="Custom",
            text_color=COLOR_DARK_GREY,
            size_hint=(None, None),
            size=(dp(STREAK_ICON_SIZE), dp(STREAK_ICON_SIZE)),
            pos_hint={"center_y": 0.55},  # Vertically center in container
        )

        self.streak_container.add_widget(self.streak_label)
        self.streak_container.add_widget(self.streak_icon)

        # Progress text (e.g., "3 / 5 times") - right-aligned, fills remaining space
        self.progress_label = MDLabel(
            text="0 / 1",
            font_style="Caption",
            theme_text_color="Secondary",
            halign="right",
            size_hint_x=1,  # Fills remaining space
            pos_hint={"center_y": 0.5}  # Center vertically
        )

        # Increment button on the right - square FAB-like button
        self.increment_btn = MDIconButton(
            icon="plus",
            icon_size=BUTTON_ICON_SIZE,
            theme_text_color="Custom",
            text_color=COLOR_LIGHT_GREY,
            size_hint=(None, None),
            size=(dp(BUTTON_TOUCH_AREA), dp(BUTTON_TOUCH_AREA)),
            pos_hint={"center_y": 0.5},
            on_release=self._on_increment_pressed,
        )

        # Add square rounded background to button (FAB-like)
        with self.increment_btn.canvas.before:
            self.btn_bg_color = Color(rgba=COLOR_DARK_GREY)
            self.btn_bg_rect = RoundedRectangle(
                pos=self.increment_btn.pos,
                size=(dp(BUTTON_BACKGROUND_SIZE), dp(BUTTON_BACKGROUND_SIZE)),
                radius=[dp(BUTTON_BACKGROUND_RADIUS)]
            )
        self.increment_btn.bind(
            pos=self._update_btn_bg_rect,
            size=self._update_btn_bg_rect
        )

        # Add all components to main layout (single row)
        main_layout.add_widget(self.name_label)
        main_layout.add_widget(self.streak_container)
        main_layout.add_widget(self.progress_label)
        main_layout.add_widget(self.increment_btn)

        self.add_widget(main_layout)

    def _update_name_bg_rect(self, *args):
        """Update the habit name background rectangle when size/position changes."""
        self.name_bg_rect.pos = self.name_label.pos
        self.name_bg_rect.size = self.name_label.size

    def _update_btn_bg_rect(self, *args):
        """Update the button background rectangle when size/position changes.
        Centers the background within the touch area."""
        # Center the background within the button's touch area
        offset = (self.increment_btn.width - dp(BUTTON_BACKGROUND_SIZE)) / 2
        self.btn_bg_rect.pos = (
            self.increment_btn.x + offset,
            self.increment_btn.y + offset
        )
        self.btn_bg_rect.size = (dp(BUTTON_BACKGROUND_SIZE), dp(BUTTON_BACKGROUND_SIZE))

    def on_habit(self, instance, value):
        """Update UI when habit data changes."""
        if value and hasattr(self, 'name_label'):
            self.update_habit_display()

    def on_progress(self, instance, value):
        """Update UI when progress data changes."""
        if value and hasattr(self, 'progress_label'):
            self.update_progress_display()

    def update_habit_display(self):
        """Update the habit-related UI elements."""
        if not self.habit:
            return

        # Update habit name (plain text, strikethrough added in update_progress_display)
        habit_name = self.habit.get("name", "Unknown Habit")
        self.name_label.text = habit_name

        # Update habit name background color
        color_hex = self.habit.get("color", "#E57373")
        try:
            color_rgb = get_color_from_hex(color_hex)
            self.name_bg_color.rgba = color_rgb
        except Exception:
            # Fallback to red if color parsing fails
            self.name_bg_color.rgba = COLOR_FALLBACK_RED

    def update_progress_display(self):
        """Update the progress-related UI elements."""
        if not self.progress:
            return

        current = self.progress.get("current_count", 0)
        goal = self.progress.get("goal_count", 1)
        goal_met = self.progress.get("goal_met", False)

        # Update progress text
        unit = "time" if goal == 1 else "times"
        self.progress_label.text = f"{current} / {goal} {unit}"

        # Update card background color based on goal_met
        if goal_met:
            self.md_bg_color = COLOR_LIGHT_GREY
        else:
            self.md_bg_color = COLOR_WHITE

        # Update habit name with strikethrough if goal met
        if self.habit:
            habit_name = self.habit.get("name", "Unknown Habit")
            if goal_met:
                self.name_label.text = f"[s]{habit_name}[/s]"  # Strikethrough markup
            else:
                self.name_label.text = habit_name  # Plain text

        # Update streak display
        streak = self.progress.get("streak", 0)
        self.streak_label.text = str(streak)

        if streak > 0:
            # Active streak - pale orange (brand flame color)
            flame_color = hex_to_rgba(BRAND_FLAME_MID)
            self.streak_label.text_color = flame_color
            self.streak_icon.text_color = flame_color
        else:
            # No streak - grey
            self.streak_label.text_color = COLOR_DARK_GREY
            self.streak_icon.text_color = COLOR_DARK_GREY

        # Update completion button icon and color based on goal_met
        if goal_met:
            # Goal met - show check icon with habit color background
            self.increment_btn.icon = "check"
            self.increment_btn.text_color = COLOR_WHITE
            self.increment_btn.disabled = True  # Disable button when goal is met

            # Set button background to habit color
            if self.habit:
                color_hex = self.habit.get("color", "#E57373")
                try:
                    color_rgb = get_color_from_hex(color_hex)
                    self.btn_bg_color.rgba = color_rgb
                except Exception:
                    self.btn_bg_color.rgba = COLOR_FALLBACK_RED
        else:
            # Goal not met - show plus icon with grey
            self.increment_btn.icon = "plus"
            self.increment_btn.text_color = COLOR_LIGHT_GREY
            self.btn_bg_color.rgba = COLOR_DARK_GREY
            self.increment_btn.disabled = False  # Enable button when goal is not met

    def _on_increment_pressed(self, button):
        """Handle increment button press."""
        from kivy.logger import Logger
        Logger.info(f"HabitCard: Increment button pressed for habit {self.habit}")
        if self.on_increment and self.habit:
            habit_id = self.habit.get("id")
            if habit_id:
                Logger.info(f"HabitCard: Calling on_increment callback with habit_id={habit_id}")
                self.on_increment(habit_id)
            else:
                Logger.warning("HabitCard: No habit_id found in habit data")
        else:
            Logger.warning(f"HabitCard: on_increment={self.on_increment}, habit={self.habit}")

    def update_data(self, habit_dict, progress_dict):
        """
        Update both habit and progress data at once.

        Args:
            habit_dict: Dictionary with habit data
            progress_dict: Dictionary with progress data
        """
        self.habit = habit_dict
        self.progress = progress_dict
