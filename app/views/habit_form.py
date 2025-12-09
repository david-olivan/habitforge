"""
Habit Form Screen for HabitForge

Screen for creating and editing habits with validation.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.logger import Logger

from models.database import create_habit, get_habit_by_id, update_habit
from logic.habit_manager import validate_habit_for_save
from components.color_picker import HabitColorPicker
from config.constants import (
    GOAL_TYPE_LABELS,
    DEFAULT_GOAL_TYPE,
    DEFAULT_GOAL_COUNT,
    DEFAULT_HABIT_COLOR,
    MIN_GOAL_COUNT,
    MAX_GOAL_COUNT,
)


class HabitFormScreen(MDScreen):
    """
    Screen for creating or editing a habit.

    Args:
        habit_id: If provided, loads and edits existing habit.
                 If None, creates a new habit.
    """

    def __init__(self, habit_id=None, **kwargs):
        super().__init__(**kwargs)
        self.habit_id = habit_id
        self.name = "habit_form"

        # Form data
        self.habit_name = ""
        self.habit_color = DEFAULT_HABIT_COLOR
        self.habit_goal_type = DEFAULT_GOAL_TYPE
        self.habit_goal_count = DEFAULT_GOAL_COUNT

        # Error messages
        self.errors = {}

        # Build UI
        self._build_ui()

        # Load habit data if editing
        if self.habit_id:
            self._load_habit_data()

    def _build_ui(self):
        """Build the form user interface."""
        # Main container
        container = MDBoxLayout(
            orientation="vertical", padding=dp(20), spacing=dp(16)
        )

        # Title
        title = MDLabel(
            text="New Habit" if not self.habit_id else "Edit Habit",
            font_style="H5",
            size_hint_y=None,
            height=dp(40),
        )
        container.add_widget(title)

        # Habit Name Field
        self.name_field = MDTextField(
            hint_text="Habit Name",
            helper_text="Enter a unique name (1-50 characters)",
            helper_text_mode="on_focus",
            max_text_length=50,
            size_hint_y=None,
            height=dp(56),
        )
        self.name_field.bind(text=self._on_name_change)
        container.add_widget(self.name_field)

        # Color Picker Section
        color_label = MDLabel(
            text="Habit Color", size_hint_y=None, height=dp(24), font_style="Subtitle1"
        )
        container.add_widget(color_label)

        self.color_picker = HabitColorPicker(selected_color=self.habit_color)
        self.color_picker.bind(selected_color=self._on_color_change)
        container.add_widget(self.color_picker)

        # Goal Type Section
        goal_type_label = MDLabel(
            text="Goal Frequency",
            size_hint_y=None,
            height=dp(24),
            font_style="Subtitle1",
        )
        container.add_widget(goal_type_label)

        # Goal Type Spinner
        self.goal_type_spinner = Spinner(
            text=GOAL_TYPE_LABELS[DEFAULT_GOAL_TYPE],
            values=list(GOAL_TYPE_LABELS.values()),
            size_hint_y=None,
            height=dp(48),
            background_color=(0.2, 0.2, 0.2, 1),
        )
        self.goal_type_spinner.bind(text=self._on_goal_type_change)
        container.add_widget(self.goal_type_spinner)

        # Goal Count Section
        goal_count_label = MDLabel(
            text="Goal Count",
            size_hint_y=None,
            height=dp(24),
            font_style="Subtitle1",
        )
        container.add_widget(goal_count_label)

        # Goal Count Input (with +/- buttons)
        goal_count_container = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8),
        )

        self.minus_btn = MDFlatButton(
            text="-", size_hint_x=0.2, on_press=self._decrement_goal
        )
        goal_count_container.add_widget(self.minus_btn)

        self.goal_count_field = MDTextField(
            text=str(DEFAULT_GOAL_COUNT),
            input_filter="int",
            size_hint_x=0.6,
            halign="center",
        )
        self.goal_count_field.bind(text=self._on_goal_count_change)
        goal_count_container.add_widget(self.goal_count_field)

        self.plus_btn = MDFlatButton(
            text="+", size_hint_x=0.2, on_press=self._increment_goal
        )
        goal_count_container.add_widget(self.plus_btn)

        container.add_widget(goal_count_container)

        # Error Display Area
        self.error_label = MDLabel(
            text="",
            theme_text_color="Error",
            size_hint_y=None,
            height=dp(40),
            font_style="Caption",
        )
        container.add_widget(self.error_label)

        # Spacer to push buttons to bottom
        container.add_widget(MDLabel())  # Spacer

        # Action Buttons
        button_container = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(12),
        )

        cancel_btn = MDFlatButton(text="Cancel", on_press=self._on_cancel)
        button_container.add_widget(cancel_btn)

        self.save_btn = MDRaisedButton(
            text="Save", on_press=self._on_save, disabled=False
        )
        button_container.add_widget(self.save_btn)

        container.add_widget(button_container)

        self.add_widget(container)

    def _load_habit_data(self):
        """Load existing habit data for editing."""
        habit = get_habit_by_id(self.habit_id)
        if habit:
            self.habit_name = habit.name
            self.habit_color = habit.color
            self.habit_goal_type = habit.goal_type
            self.habit_goal_count = habit.goal_count

            # Update UI
            self.name_field.text = habit.name
            self.color_picker.set_color(habit.color)
            self.goal_type_spinner.text = GOAL_TYPE_LABELS[habit.goal_type]
            self.goal_count_field.text = str(habit.goal_count)

            Logger.info(f"HabitForm: Loaded habit ID {self.habit_id} for editing")
        else:
            Logger.error(f"HabitForm: Failed to load habit ID {self.habit_id}")

    def _on_name_change(self, instance, value):
        """Handle habit name change."""
        self.habit_name = value
        # Clear error when user starts typing
        if "name" in self.errors:
            del self.errors["name"]
            self._update_error_display()

    def _on_color_change(self, instance, value):
        """Handle color selection change."""
        self.habit_color = value
        Logger.info(f"HabitForm: Color changed to {value}")

    def _on_goal_type_change(self, instance, value):
        """Handle goal type change."""
        # Convert label back to value
        for key, label in GOAL_TYPE_LABELS.items():
            if label == value:
                self.habit_goal_type = key
                Logger.info(f"HabitForm: Goal type changed to {key}")
                break

    def _on_goal_count_change(self, instance, value):
        """Handle goal count change."""
        try:
            count = int(value) if value else DEFAULT_GOAL_COUNT
            self.habit_goal_count = max(MIN_GOAL_COUNT, min(count, MAX_GOAL_COUNT))
            # Clear error when user changes value
            if "goal_count" in self.errors:
                del self.errors["goal_count"]
                self._update_error_display()
        except ValueError:
            pass

    def _increment_goal(self, instance):
        """Increment goal count."""
        current = int(self.goal_count_field.text or DEFAULT_GOAL_COUNT)
        new_value = min(current + 1, MAX_GOAL_COUNT)
        self.goal_count_field.text = str(new_value)

    def _decrement_goal(self, instance):
        """Decrement goal count."""
        current = int(self.goal_count_field.text or DEFAULT_GOAL_COUNT)
        new_value = max(current - 1, MIN_GOAL_COUNT)
        self.goal_count_field.text = str(new_value)

    def _update_error_display(self):
        """Update the error message display."""
        if self.errors:
            error_messages = []
            for field, message in self.errors.items():
                error_messages.append(f"{field.title()}: {message}")
            self.error_label.text = "\n".join(error_messages)
        else:
            self.error_label.text = ""

    def _on_save(self, instance):
        """Handle save button press."""
        # Collect form data
        habit_data = {
            "name": self.habit_name,
            "color": self.habit_color,
            "goal_type": self.habit_goal_type,
            "goal_count": int(self.goal_count_field.text or DEFAULT_GOAL_COUNT),
        }

        # Validate data
        is_valid, errors = validate_habit_for_save(habit_data, self.habit_id)

        if not is_valid:
            # Show validation errors
            self.errors = errors
            self._update_error_display()
            Logger.warning(f"HabitForm: Validation failed: {errors}")
            return

        # Save to database
        try:
            if self.habit_id:
                # Update existing habit
                success = update_habit(self.habit_id, **habit_data)
                if success:
                    Logger.info(f"HabitForm: Updated habit ID {self.habit_id}")
                    self._on_success("Habit updated successfully!")
                else:
                    self._show_error("Failed to update habit")
            else:
                # Create new habit
                new_id = create_habit(**habit_data)
                Logger.info(f"HabitForm: Created new habit ID {new_id}")
                self._on_success("Habit created successfully!")

        except Exception as e:
            Logger.error(f"HabitForm: Error saving habit: {e}")
            self._show_error(f"Error saving habit: {str(e)}")

    def _on_cancel(self, instance):
        """Handle cancel button press."""
        Logger.info("HabitForm: Cancelled")
        self._reset_form()
        self._navigate_to_main()

    def _reset_form(self):
        """Reset the form to defaults."""
        self.name_field.text = ""
        self.color_picker.set_color(DEFAULT_HABIT_COLOR)
        self.goal_type_spinner.text = GOAL_TYPE_LABELS[DEFAULT_GOAL_TYPE]
        self.goal_count_field.text = str(DEFAULT_GOAL_COUNT)
        self.errors = {}
        self._update_error_display()

    def _on_success(self, message: str):
        """Handle successful save."""
        Logger.info(f"HabitForm: {message}")
        # Show success message
        self.error_label.text = message
        self.error_label.theme_text_color = "Custom"
        self.error_label.text_color = (0, 1, 0, 1)  # Green

        # Reset form and navigate back after short delay
        from kivy.clock import Clock

        Clock.schedule_once(lambda dt: self._reset_and_navigate(), 1.5)

    def _reset_and_navigate(self):
        """Reset form and navigate back to main screen."""
        self._reset_form()
        self._navigate_to_main()

    def _navigate_to_main(self):
        """Navigate back to main container screen."""
        if self.manager:
            self.manager.current = "main_container"
            # Refresh the habits list to show new/updated habit
            main_container = self.manager.get_screen("main_container")
            if main_container and hasattr(main_container, "habits_screen"):
                habits_screen = main_container.habits_screen
                if hasattr(habits_screen, "refresh_on_return"):
                    habits_screen.refresh_on_return()

    def _show_error(self, message: str):
        """Show error message."""
        Logger.error(f"HabitForm: {message}")
        self.error_label.text = message
        self.error_label.theme_text_color = "Error"