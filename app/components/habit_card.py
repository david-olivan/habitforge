"""
Habit Card Component for HabitForge

A reusable card widget that displays a habit with its progress,
goal information, and an increment button.
"""

from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.properties import DictProperty, ObjectProperty, NumericProperty
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from config.constants import GOAL_TYPE_LABELS


class HabitCard(MDCard):
    """
    A card widget displaying habit information and progress.

    Shows:
    - Colored vertical bar on left
    - Habit name and goal type
    - Progress (current/goal count)
    - Goal met indicator
    - Increment button
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
        self.height = dp(80)
        self.md_bg_color = (1, 1, 1, 1)  # White background
        self.elevation = 2
        self.radius = [dp(8)]
        self.padding = dp(0)

        # Build the UI
        self.build_ui()

    def build_ui(self):
        """Build the card UI layout."""
        # Main container
        main_layout = MDBoxLayout(
            orientation="horizontal", spacing=dp(12), padding=[dp(4), dp(8), dp(8), dp(8)]
        )

        # Colored bar on the left
        self.color_bar = MDBoxLayout(size_hint_x=None, width=dp(6))
        with self.color_bar.canvas.before:
            self.bar_color = Color(rgba=(0.9, 0.3, 0.3, 1))  # Default red
            self.bar_rect = Rectangle(pos=self.color_bar.pos, size=self.color_bar.size)
        self.color_bar.bind(pos=self.update_bar_rect, size=self.update_bar_rect)

        # Content area (habit info)
        content_layout = MDBoxLayout(orientation="vertical", spacing=dp(4))

        # Habit name (bold, larger text)
        self.name_label = MDLabel(
            text="Habit Name",
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(24),
        )

        # Goal type and progress container
        info_layout = MDBoxLayout(
            orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(20)
        )

        # Goal type label
        self.goal_type_label = MDLabel(
            text="Daily",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_x=None,
            width=dp(60),
        )

        # Progress text (e.g., "3 / 5 times")
        self.progress_label = MDLabel(
            text="0 / 1",
            font_style="Caption",
            theme_text_color="Secondary",
        )

        info_layout.add_widget(self.goal_type_label)
        info_layout.add_widget(self.progress_label)

        # Goal met indicator
        self.goal_met_label = MDLabel(
            text="",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.3, 0.7, 0.3, 1),  # Green
            size_hint_y=None,
            height=dp(20),
        )

        content_layout.add_widget(self.name_label)
        content_layout.add_widget(info_layout)
        content_layout.add_widget(self.goal_met_label)

        # Increment button on the right
        self.increment_btn = MDIconButton(
            icon="plus-circle",
            theme_text_color="Custom",
            text_color=(0.3, 0.6, 0.9, 1),  # Blue
            on_release=self._on_increment_pressed,
        )

        # Add all components to main layout
        main_layout.add_widget(self.color_bar)
        main_layout.add_widget(content_layout)
        main_layout.add_widget(self.increment_btn)

        self.add_widget(main_layout)

    def update_bar_rect(self, *args):
        """Update the colored bar rectangle when size/position changes."""
        self.bar_rect.pos = self.color_bar.pos
        self.bar_rect.size = self.color_bar.size

    def on_habit(self, instance, value):
        """Update UI when habit data changes."""
        if value:
            self.update_habit_display()

    def on_progress(self, instance, value):
        """Update UI when progress data changes."""
        if value:
            self.update_progress_display()

    def update_habit_display(self):
        """Update the habit-related UI elements."""
        if not self.habit:
            return

        # Update habit name
        self.name_label.text = self.habit.get("name", "Unknown Habit")

        # Update goal type label
        goal_type = self.habit.get("goal_type", "daily")
        self.goal_type_label.text = GOAL_TYPE_LABELS.get(goal_type, "Daily")

        # Update color bar
        color_hex = self.habit.get("color", "#E57373")
        try:
            color_rgb = get_color_from_hex(color_hex)
            self.bar_color.rgba = color_rgb
        except Exception:
            # Fallback to red if color parsing fails
            self.bar_color.rgba = (0.9, 0.3, 0.3, 1)

    def update_progress_display(self):
        """Update the progress-related UI elements."""
        if not self.progress:
            return

        current = self.progress.get("current_count", 0)
        goal = self.progress.get("goal_count", 1)
        goal_met = self.progress.get("goal_met", False)

        # Update progress text
        goal_type = self.habit.get("goal_type", "daily") if self.habit else "daily"
        unit = "time" if goal == 1 else "times"
        self.progress_label.text = f"{current} / {goal} {unit}"

        # Update goal met indicator
        if goal_met:
            self.goal_met_label.text = "✓ Goal met!"
        else:
            self.goal_met_label.text = ""

    def _on_increment_pressed(self, button):
        """Handle increment button press."""
        if self.on_increment and self.habit:
            habit_id = self.habit.get("id")
            if habit_id:
                self.on_increment(habit_id)

    def update_data(self, habit_dict, progress_dict):
        """
        Update both habit and progress data at once.

        Args:
            habit_dict: Dictionary with habit data
            progress_dict: Dictionary with progress data
        """
        self.habit = habit_dict
        self.progress = progress_dict
