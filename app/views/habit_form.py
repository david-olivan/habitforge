"""
Habit Form Screen for HabitForge

Screen for creating and editing habits with validation and modern UI.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp
from kivy.logger import Logger
from kivy.graphics import Color, RoundedRectangle

from models.database import create_habit, get_habit_by_id, update_habit
from logic.habit_manager import validate_habit_for_save
from logic.localization import _
from components.color_picker_button import ColorPickerButton
from config.constants import (
    GOAL_TYPE_LABELS,
    DEFAULT_GOAL_TYPE,
    DEFAULT_GOAL_COUNT,
    DEFAULT_HABIT_COLOR,
    MIN_GOAL_COUNT,
    MAX_GOAL_COUNT,
    BRAND_PRIMARY_RGB,
    hex_to_rgba,
    BRAND_FLAME_MID,
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
        # Main vertical layout
        main_layout = MDBoxLayout(orientation="vertical")

        # Add orange header bar
        toolbar = MDTopAppBar(
            title=_("habits.edit_habit") if self.habit_id else _("habits.new_habit"),
            md_bg_color=BRAND_PRIMARY_RGB,
            specific_text_color=(1, 1, 1, 1),  # White text
            elevation=0,
            size_hint_y=None,
            height=dp(56),
        )
        main_layout.add_widget(toolbar)

        # Scrollable content area
        scroll_view = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(24), dp(20), dp(8)],
            spacing=dp(20),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        # === Name Input Block ===
        name_block = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            spacing=dp(12),
            padding=[dp(12), 0, dp(12), 0]
        )
        # Add white background and gray border using canvas
        with name_block.canvas.before:
            Color(1, 1, 1, 1)  # White background
            name_block.bg_rect = RoundedRectangle(
                pos=name_block.pos,
                size=name_block.size,
                radius=[dp(8)]
            )
            Color(0.9, 0.9, 0.9, 1)  # Light gray border
            name_block.border_rect = RoundedRectangle(
                pos=name_block.pos,
                size=name_block.size,
                radius=[dp(8)]
            )
        name_block.bind(
            pos=lambda *args: [
                setattr(name_block.bg_rect, 'pos', name_block.pos),
                setattr(name_block.border_rect, 'pos', name_block.pos)
            ]
        )
        name_block.bind(
            size=lambda *args: [
                setattr(name_block.bg_rect, 'size', name_block.size),
                setattr(name_block.border_rect, 'size', name_block.size)
            ]
        )

        name_label = MDLabel(
            text=_("habits.name_label") if _("habits.name_label") != "habits.name_label" else "Name",
            size_hint_x=0.3,
            font_style="Subtitle1",
            pos_hint={"center_y": 0.5}
        )

        self.name_field = MDTextField(
            hint_text=_("habits.habit_name"),
            max_text_length=26,  # UI limit (database still 50)
            size_hint_x=0.7,
            pos_hint={"center_y": 0.5}
        )
        self.name_field.bind(text=self._on_name_change)

        name_block.add_widget(name_label)
        name_block.add_widget(self.name_field)
        content.add_widget(name_block)

        # === Color Picker Block ===
        color_block = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            spacing=dp(12),
            padding=[dp(12), 0, dp(12), 0]
        )
        # Add white background and gray border using canvas
        with color_block.canvas.before:
            Color(1, 1, 1, 1)  # White background
            color_block.bg_rect = RoundedRectangle(
                pos=color_block.pos,
                size=color_block.size,
                radius=[dp(8)]
            )
            Color(0.9, 0.9, 0.9, 1)  # Light gray border
            color_block.border_rect = RoundedRectangle(
                pos=color_block.pos,
                size=color_block.size,
                radius=[dp(8)]
            )
        color_block.bind(
            pos=lambda *args: [
                setattr(color_block.bg_rect, 'pos', color_block.pos),
                setattr(color_block.border_rect, 'pos', color_block.pos)
            ]
        )
        color_block.bind(
            size=lambda *args: [
                setattr(color_block.bg_rect, 'size', color_block.size),
                setattr(color_block.border_rect, 'size', color_block.size)
            ]
        )

        color_label = MDLabel(
            text=_("habits.habit_color"),
            size_hint_x=0.3,
            font_style="Subtitle1",
            pos_hint={"center_y": 0.5}
        )

        self.color_button = ColorPickerButton(
            selected_color=self.habit_color,
            size_hint_x=0.7,
            pos_hint={"center_y": 0.5}
        )
        self.color_button.bind(selected_color=self._on_color_change)

        color_block.add_widget(color_label)
        color_block.add_widget(self.color_button)
        content.add_widget(color_block)

        # === Frequency Section (Vertical Stack) ===
        freq_section = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(112),
            spacing=dp(6),
            padding=[dp(12), dp(6), dp(12), dp(6)]
        )
        # Add white background and gray border to frequency section
        with freq_section.canvas.before:
            Color(1, 1, 1, 1)  # White background
            freq_section.bg_rect = RoundedRectangle(
                pos=freq_section.pos,
                size=freq_section.size,
                radius=[dp(8)]
            )
            Color(0.9, 0.9, 0.9, 1)  # Light gray border
            freq_section.border_rect = RoundedRectangle(
                pos=freq_section.pos,
                size=freq_section.size,
                radius=[dp(8)]
            )
        freq_section.bind(
            pos=lambda *args: [
                setattr(freq_section.bg_rect, 'pos', freq_section.pos),
                setattr(freq_section.border_rect, 'pos', freq_section.pos)
            ]
        )
        freq_section.bind(
            size=lambda *args: [
                setattr(freq_section.bg_rect, 'size', freq_section.size),
                setattr(freq_section.border_rect, 'size', freq_section.size)
            ]
        )

        # Line 1: "Frequency of" + spinner
        freq_of_block = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(12)
        )

        freq_label = MDLabel(
            text=_("habits.frequency_of"),
            size_hint_x=0.5,
            font_style="Subtitle1",
            pos_hint={"center_y": 0.5}
        )

        spinner_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=0.5,
            spacing=dp(4),
            pos_hint={"center_y": 0.5}
        )

        self.minus_btn = MDIconButton(
            icon="minus",
            on_press=self._decrement_goal
        )

        self.goal_count_field = MDTextField(
            text=str(DEFAULT_GOAL_COUNT),
            input_filter="int",
            halign="center",
            size_hint_x=None,
            width=dp(60)
        )
        self.goal_count_field.bind(text=self._on_goal_count_change)

        self.plus_btn = MDIconButton(
            icon="plus",
            on_press=self._increment_goal
        )

        spinner_box.add_widget(self.minus_btn)
        spinner_box.add_widget(self.goal_count_field)
        spinner_box.add_widget(self.plus_btn)

        freq_of_block.add_widget(freq_label)
        freq_of_block.add_widget(spinner_box)
        freq_section.add_widget(freq_of_block)

        # Line 2: "per" + dropdown
        per_block = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(4)
        )

        per_label = MDLabel(
            text=_("habits.per"),
            size_hint_x=None,
            width=dp(60),
            font_style="Subtitle1",
            pos_hint={"center_y": 0.5}
        )

        # Create dropdown button with secondary brand color background
        self.goal_type_button = MDRaisedButton(
            text=_("habits.day"),
            size_hint_x=1,
            md_bg_color=hex_to_rgba(BRAND_FLAME_MID),  # Secondary brand color (yellow-orange)
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1),  # Dark gray text for better contrast
            pos_hint={"center_y": 0.5},
            on_release=self._show_goal_type_menu
        )

        # Create dropdown menu
        self._create_goal_type_menu()

        per_block.add_widget(per_label)
        per_block.add_widget(self.goal_type_button)
        freq_section.add_widget(per_block)

        content.add_widget(freq_section)

        # === Archive Button (Edit Mode Only) ===
        if self.habit_id:
            archive_btn = MDRaisedButton(
                text=_("habits.archive"),
                size_hint_x=None,
                md_bg_color=(1, 0.98, 0.8, 1),  # Very light yellow background
                theme_text_color="Custom",
                text_color=(0.5, 0.5, 0.5, 1),  # Grey text
                font_size="16sp",  # Slightly larger text
                padding=[dp(56), dp(28)],  # More padding
                on_press=self._on_archive
            )
            # Center the archive button
            archive_container = AnchorLayout(
                size_hint=(1, None),
                height=dp(56),  # Increased height for larger button
                anchor_x="center",
                anchor_y="center"
            )
            archive_container.add_widget(archive_btn)
            content.add_widget(archive_container)

        # === Error Display ===
        self.error_label = MDLabel(
            text="",
            theme_text_color="Error",
            size_hint_y=None,
            height=dp(40),
            font_style="Caption"
        )
        content.add_widget(self.error_label)

        # Spacer to push content if needed
        content.add_widget(MDLabel(size_hint_y=None, height=dp(20)))

        scroll_view.add_widget(content)
        main_layout.add_widget(scroll_view)

        # === Bottom Buttons (Fixed, Outside Scroll) ===
        # AnchorLayout for easy centering with bottom margin for Android nav bar
        button_anchor = AnchorLayout(
            size_hint=(1, None),
            height=dp(104),  # Increased height for more spacing
            anchor_x="center",
            anchor_y="center",
            padding=[0, 0, 0, dp(24)]  # 24dp bottom padding for Android nav bar
        )

        # Button container - auto-sizes based on children
        button_container = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            spacing=dp(16)
        )
        button_container.bind(minimum_width=button_container.setter('width'))

        back_btn = MDRaisedButton(
            text=_("habits.back"),
            size_hint_x=None,
            md_bg_color=(0.85, 0.85, 0.85, 1),  # Light gray background
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1),  # Dark gray text
            padding=[dp(48), dp(24)],  # 50% more padding (was 32/16, now 48/24)
            on_press=self._on_cancel
        )

        self.add_btn = MDRaisedButton(
            text=_("habits.save") if self.habit_id else _("habits.add"),
            size_hint_x=None,
            md_bg_color=BRAND_PRIMARY_RGB,  # Brand orange
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),  # White text
            padding=[dp(48), dp(24)],  # 50% more padding (was 32/16, now 48/24)
            on_press=self._on_save
        )

        button_container.add_widget(back_btn)
        button_container.add_widget(self.add_btn)
        button_anchor.add_widget(button_container)

        main_layout.add_widget(button_anchor)
        self.add_widget(main_layout)

    def _create_goal_type_menu(self):
        """Create dropdown menu for goal type selection."""
        menu_items = [
            {
                "text": _("habits.day"),
                "viewclass": "OneLineListItem",
                "on_release": lambda: self._select_goal_type("daily", _("habits.day"))
            },
            {
                "text": _("habits.week"),
                "viewclass": "OneLineListItem",
                "on_release": lambda: self._select_goal_type("weekly", _("habits.week"))
            },
            {
                "text": _("habits.month"),
                "viewclass": "OneLineListItem",
                "on_release": lambda: self._select_goal_type("monthly", _("habits.month"))
            }
        ]

        self.goal_type_menu = MDDropdownMenu(
            caller=self.goal_type_button,
            items=menu_items,
            width_mult=3
        )

    def _show_goal_type_menu(self, instance):
        """Show goal type dropdown menu."""
        self.goal_type_menu.open()

    def _select_goal_type(self, value, display_text):
        """
        Handle goal type selection.

        Args:
            value: Internal goal type value ("daily", "weekly", "monthly")
            display_text: Localized display text ("Day", "Week", "Month")
        """
        self.habit_goal_type = value
        self.goal_type_button.text = display_text
        self.goal_type_menu.dismiss()
        Logger.info(f"HabitForm: Goal type changed to {value}")

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
            self.color_button.selected_color = habit.color

            # Update goal type button with localized text
            type_display = {
                "daily": _("habits.day"),
                "weekly": _("habits.week"),
                "monthly": _("habits.month")
            }
            self.goal_type_button.text = type_display.get(habit.goal_type, _("habits.day"))

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
        """Handle cancel/back button press."""
        Logger.info("HabitForm: Cancelled")
        self._reset_form()
        self._navigate_to_main()

    def _on_archive(self, instance):
        """Handle archive button press."""
        if not self.habit_id:
            Logger.warning("HabitForm: Archive called but no habit_id")
            return

        from models.database import archive_habit

        try:
            success = archive_habit(self.habit_id)
            if success:
                Logger.info(f"HabitForm: Archived habit ID {self.habit_id}")
                self._on_success(_("messages.habit_archived"))
            else:
                self._show_error(_("messages.archive_error"))
        except Exception as e:
            Logger.error(f"HabitForm: Error archiving habit: {e}")
            self._show_error(f"Error archiving habit: {str(e)}")

    def _reset_form(self):
        """Reset the form to defaults."""
        self.name_field.text = ""
        self.color_button.selected_color = DEFAULT_HABIT_COLOR
        self.goal_type_button.text = _("habits.day")
        self.habit_goal_type = DEFAULT_GOAL_TYPE
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
