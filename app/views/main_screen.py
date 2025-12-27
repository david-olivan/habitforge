"""
Main Screen for HabitForge

Displays the list of all habits grouped by type (Daily, Weekly, Monthly)
with progress tracking and completion buttons.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import date

from models.database import get_all_habits
from logic.completion_manager import log_completion, get_habit_progress
from logic.streak_calculator import calculate_streak
from components.habit_card import HabitCard
from components.date_strip import DateNavigationStrip, STRIP_HEIGHT
from config.constants import GOAL_TYPE_LABELS, BRAND_PRIMARY_RGB
from logic.localization import _
from kivy.logger import Logger


class MainScreen(MDScreen):
    """
    Main screen showing all habits grouped by type.

    Features:
    - Top app bar with title
    - Scrollable list of habits
    - Grouped sections (Daily, Weekly, Monthly)
    - FAB button to add new habits
    """

    def __init__(self, embedded=False, **kwargs):
        super().__init__(**kwargs)
        self.name = "main_screen"
        self.embedded = embedded  # Whether screen is embedded in bottom nav

        # Data storage
        self.habits = []
        self.daily_habits = []
        self.weekly_habits = []
        self.monthly_habits = []
        self.progress_data = {}
        self.habit_cards = {}  # Map habit_id to HabitCard widget
        self.section_collapsed = {}  # Track collapsed state per section (Daily/Weekly/Monthly)
        self.section_widgets = {}  # Map section title to section widget for dynamic updates

        # Date selection state (for 5-day navigation)
        self.selected_date = date.today()

        # Build UI
        self.build_ui()

    def build_ui(self):
        """Build the main screen UI."""
        # Main container - vertical layout for toolbar + content
        main_layout = MDBoxLayout(orientation="vertical")

        # Top app bar (only show if not embedded in bottom nav)
        if not self.embedded:
            self.toolbar = MDTopAppBar(
                title="HabitForge",
                md_bg_color=(0.3, 0.6, 0.9, 1),  # Blue
                specific_text_color=(1, 1, 1, 1),  # White text
            )
            main_layout.add_widget(self.toolbar)

        # Float layout to hold scroll and FAB (FAB floats above scroll)
        float_container = FloatLayout()

        # Scrollable content area (fills the float layout)
        scroll = MDScrollView(size_hint=(1, 1))
        self.content_layout = MDBoxLayout(
            orientation="vertical", spacing=dp(16), padding=dp(16), size_hint_y=None
        )
        self.content_layout.bind(
            minimum_height=self.content_layout.setter("height")
        )  # Make scrollable

        # Date navigation strip (5-day selector)
        # Center it by setting size_hint_x=None and wrapping in a centered container
        self.date_strip = DateNavigationStrip(selected_date=self.selected_date)
        self.date_strip.on_date_changed = self._on_date_selected
        self.date_strip.size_hint_x = None  # Don't expand to fill width

        # Calculate strip width: 5 buttons + 4 gaps + horizontal padding
        strip_width = (5 * 58) + (4 * 6) + (2 * 12)  # buttons + spacing + padding
        self.date_strip.width = dp(strip_width)

        # Wrap in horizontal container with spacers to center the strip
        strip_container = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(STRIP_HEIGHT)
        )
        strip_container.add_widget(Widget())  # Left spacer
        strip_container.add_widget(self.date_strip)
        strip_container.add_widget(Widget())  # Right spacer
        self.content_layout.add_widget(strip_container)

        # Placeholder for habit sections (will be populated in on_enter)
        self.sections_container = MDBoxLayout(
            orientation="vertical", spacing=dp(24), size_hint_y=None
        )
        self.sections_container.bind(
            minimum_height=self.sections_container.setter("height")
        )
        self.content_layout.add_widget(self.sections_container)

        scroll.add_widget(self.content_layout)
        float_container.add_widget(scroll)

        # FAB button (Add Habit) - floats above scroll
        # Adjust position to avoid bottom nav and safe area overlap when embedded
        # Bottom safe area (5%) + bottom nav (~8%) = 13% total clearance needed
        fab_y_pos = 0.13 if self.embedded else 0.15  # More distance from bottom nav and safe area
        self.fab = MDFloatingActionButton(
            icon="plus",
            md_bg_color=BRAND_PRIMARY_RGB,  # Brand orange
            pos_hint={"center_x": 0.9, "center_y": fab_y_pos},
            on_release=self.navigate_to_add_habit,
        )
        if hasattr(self.fab, 'elevation'):
            self.fab.elevation = 6  # Proper elevation for floating effect

        # Add FAB to float layout (it will float above scroll)
        float_container.add_widget(self.fab)

        # Assemble layout
        main_layout.add_widget(float_container)

        self.add_widget(main_layout)

    def _format_today(self) -> str:
        """Format today's date as 'Day, Month Date'."""
        today = date.today()
        return today.strftime("Today: %A, %b %d")

    def _get_icon_for_section(self, title: str) -> str:
        """
        Get the appropriate Material Design icon for a section title.

        Args:
            title: Section title (e.g., "Daily Goals")

        Returns:
            Icon name for KivyMD
        """
        if "Daily" in title:
            return "calendar-today"
        elif "Weekly" in title:
            return "calendar-week"
        elif "Monthly" in title:
            return "calendar-month"
        else:
            return "calendar-blank"  # Fallback

    def on_enter(self, *args):
        """Called when screen is displayed."""
        Logger.info("MainScreen: Screen entered, loading habits")
        self.load_habits()

    def load_habits(self):
        """Load all habits from database and group by type."""
        Logger.info("MainScreen: Loading habits from database")

        # Clear existing data
        self.habits = []
        self.daily_habits = []
        self.weekly_habits = []
        self.monthly_habits = []
        self.progress_data = {}
        self.habit_cards = {}

        # Query all active habits
        self.habits = get_all_habits(include_archived=False)

        # Group by goal_type
        for habit in self.habits:
            if habit.goal_type == "daily":
                self.daily_habits.append(habit)
            elif habit.goal_type == "weekly":
                self.weekly_habits.append(habit)
            elif habit.goal_type == "monthly":
                self.monthly_habits.append(habit)

        # Sort habits by creation date (newest first)
        self.daily_habits.sort(key=lambda h: h.created_at, reverse=True)
        self.weekly_habits.sort(key=lambda h: h.created_at, reverse=True)
        self.monthly_habits.sort(key=lambda h: h.created_at, reverse=True)

        Logger.info(
            f"MainScreen: Loaded {len(self.habits)} habits "
            f"(daily={len(self.daily_habits)}, weekly={len(self.weekly_habits)}, monthly={len(self.monthly_habits)})"
        )

        # Load progress for all habits
        self.load_progress_data()

        # Render the UI
        self.render_habit_sections()

    def load_progress_data(self):
        """Calculate progress and streaks for all habits using selected_date."""
        for habit in self.habits:
            # Calculate progress for selected date
            progress = get_habit_progress(
                habit.id, habit.goal_count, habit.goal_type, self.selected_date
            )

            # Calculate streak (always uses today, not selected_date)
            streak = calculate_streak(habit.id, habit.goal_type, habit.goal_count)
            progress['streak'] = streak

            self.progress_data[habit.id] = progress
            Logger.debug(
                f"MainScreen: Progress for '{habit.name}' on {self.selected_date}: {progress['current_count']}/{progress['goal_count']}, Streak: {streak}"
            )

    def render_habit_sections(self):
        """Render the habit sections (Daily, Weekly, Monthly)."""
        # Clear existing sections
        self.sections_container.clear_widgets()

        # Show empty state if no habits
        if not self.habits:
            self.show_empty_state()
            return

        # Render Daily section
        if self.daily_habits:
            self.render_section(_("habits.daily_section"), self.daily_habits)

        # Render Weekly section
        if self.weekly_habits:
            self.render_section(_("habits.weekly_section"), self.weekly_habits)

        # Render Monthly section
        if self.monthly_habits:
            self.render_section(_("habits.monthly_section"), self.monthly_habits)

        # Add bottom spacer to prevent FAB from covering last habit's buttons
        # FAB clearance: 56dp (FAB) + 16dp (margin) + 16dp (safe scroll) = 88dp
        from kivy.uix.widget import Widget
        spacer = Widget(size_hint_y=None, height=dp(88))
        self.sections_container.add_widget(spacer)

    def render_section(self, title: str, habits: list):
        """
        Render a section with a title and habit cards.

        Args:
            title: Section title (e.g., "Daily Goals")
            habits: List of Habit objects to display
        """
        # Section container
        section = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        section.bind(minimum_height=section.setter("height"))

        # Section header with icon
        header_container = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(26),
        )

        # Determine icon based on title
        icon_name = self._get_icon_for_section(title)

        # Icon
        from kivymd.uix.label import MDIcon
        icon = MDIcon(
            icon=icon_name,
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, 1),
            size_hint=(None, 1),  # Take full height for vertical alignment
            width=dp(28),
            halign="left",
            valign="center",
            pos_hint={"center_y": 0.5},
        )
        header_container.add_widget(icon)

        # Title label
        header = MDLabel(
            text=f"{title} ({len(habits)})",
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(26),
            valign="center",
        )
        header_container.add_widget(header)

        # Chevron button for collapse/expand
        is_collapsed = self.section_collapsed.get(title, False)
        chevron_icon = "chevron-right" if is_collapsed else "chevron-down"
        chevron_button = MDIconButton(
            icon=chevron_icon,
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, 1),
            size_hint=(None, 1),
            width=dp(32),
            pos_hint={"center_y": 0.5},
        )
        # Bind the toggle action - pass title, section, habits list, and chevron button
        chevron_button.bind(on_release=lambda btn: self.toggle_section(title, section, habits, btn))
        header_container.add_widget(chevron_button)

        section.add_widget(header_container)

        # Store section widget for dynamic updates
        self.section_widgets[title] = section

        # Habit cards (only render if section is not collapsed)
        if not is_collapsed:
            for habit in habits:
                habit_dict = {
                    "id": habit.id,
                    "name": habit.name,
                    "color": habit.color,
                    "goal_type": habit.goal_type,
                    "goal_count": habit.goal_count,
                }
                progress_dict = self.progress_data.get(habit.id, {})

                Logger.debug(f"MainScreen: Creating card with on_increment callback: {self.on_increment}")
                card = HabitCard(habit=habit_dict, progress=progress_dict)
                card.on_increment = self.on_increment  # Set after creation
                Logger.debug(f"MainScreen: Card created, card.on_increment={card.on_increment}")
                self.habit_cards[habit.id] = card
                section.add_widget(card)

        self.sections_container.add_widget(section)

    def show_empty_state(self):
        """Show empty state when no habits exist."""
        empty_label = MDLabel(
            text="No habits yet!\nTap the + button to add your first habit.",
            halign="center",
            theme_text_color="Secondary",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(100),
        )
        self.sections_container.add_widget(empty_label)

    def on_increment(self, habit_id: int):
        """
        Handle increment button press on a habit card.

        Logs completion for the currently selected_date.

        Args:
            habit_id: The ID of the habit to increment
        """
        Logger.info(f"MainScreen: Increment requested for habit ID {habit_id} on {self.selected_date}")

        # Log the completion for the selected date
        success, error, completion = log_completion(habit_id, completion_date=self.selected_date)

        if success:
            Logger.info(f"MainScreen: Completion logged successfully for {self.selected_date}")
            # Refresh progress for this habit
            self.refresh_habit_progress(habit_id)
        else:
            Logger.error(f"MainScreen: Failed to log completion: {error}")
            self.show_error(error or "Failed to log completion")

    def refresh_habit_progress(self, habit_id: int):
        """
        Reload progress for a single habit and update its card using selected_date.

        Args:
            habit_id: The ID of the habit to refresh
        """
        # Find the habit
        habit = next((h for h in self.habits if h.id == habit_id), None)
        if not habit:
            Logger.warning(f"MainScreen: Habit ID {habit_id} not found for refresh")
            return

        # Recalculate progress for selected date
        progress = get_habit_progress(habit.id, habit.goal_count, habit.goal_type, self.selected_date)

        # Recalculate streak (same as load_progress_data)
        streak = calculate_streak(habit.id, habit.goal_type, habit.goal_count)
        progress['streak'] = streak

        self.progress_data[habit_id] = progress

        # Update the card
        card = self.habit_cards.get(habit_id)
        if card:
            card.progress = progress
            Logger.debug(
                f"MainScreen: Updated card for habit '{habit.name}' with new progress for {self.selected_date} (streak: {streak})"
            )

    def show_error(self, message: str):
        """
        Show an error message to the user.

        Args:
            message: Error message to display
        """
        # For now, just log it. In future, could show a Snackbar
        Logger.error(f"MainScreen: Error - {message}")
        # TODO: Implement Snackbar or Toast notification

    def toggle_section(self, section_title: str, section_widget, habits: list, chevron_button):
        """
        Toggle collapse/expand for a habit section.

        Args:
            section_title: Title of the section (e.g., "Daily Goals")
            section_widget: The section's MDBoxLayout widget
            habits: List of habits in this section
            chevron_button: The MDIconButton chevron to update
        """
        # Toggle collapsed state
        current_state = self.section_collapsed.get(section_title, False)
        new_state = not current_state
        self.section_collapsed[section_title] = new_state

        Logger.info(f"MainScreen: Toggling section '{section_title}' - collapsed={new_state}")

        # Update chevron icon
        chevron_button.icon = "chevron-right" if new_state else "chevron-down"

        # Clear section widgets (keep header, remove habit cards)
        # The section has: [header_container, habit_card1, habit_card2, ...]
        # We want to keep only the header_container at index 0
        while len(section_widget.children) > 1:
            section_widget.remove_widget(section_widget.children[0])  # Remove from top (last added)

        # If expanding, re-add habit cards
        if not new_state:
            for habit in habits:
                habit_dict = {
                    "id": habit.id,
                    "name": habit.name,
                    "color": habit.color,
                    "goal_type": habit.goal_type,
                    "goal_count": habit.goal_count,
                }
                progress_dict = self.progress_data.get(habit.id, {})

                card = HabitCard(habit=habit_dict, progress=progress_dict)
                card.on_increment = self.on_increment
                self.habit_cards[habit.id] = card
                section_widget.add_widget(card)

    def navigate_to_add_habit(self, button):
        """Navigate to the habit form screen to add a new habit."""
        Logger.info("MainScreen: Navigating to habit form")

        # Get the App instance to access the root screen manager
        from kivy.app import App
        app = App.get_running_app()
        if app and app.root:
            Logger.info("MainScreen: Found app root screen manager, switching to habit_form")
            app.root.current = "habit_form"
        else:
            Logger.error("MainScreen: Could not find app root screen manager")

    def refresh_on_return(self):
        """
        Refresh the habit list when returning from another screen.

        Call this method when navigating back to ensure the list is up-to-date.
        """
        Logger.info("MainScreen: Refreshing habits after return")
        self.load_habits()

    def _on_date_selected(self, new_date: date):
        """
        Handle date change from DateNavigationStrip.

        Reloads all progress data for the new selected date and refreshes all habit cards.

        Args:
            new_date: The newly selected date
        """
        Logger.info(f"MainScreen: Date changed to {new_date}")
        self.selected_date = new_date

        # Reload all progress for the new date
        self.load_progress_data()

        # Update all habit cards with new progress
        for habit_id, card in self.habit_cards.items():
            progress = self.progress_data.get(habit_id, {})
            card.progress = progress
            Logger.debug(f"MainScreen: Updated card for habit ID {habit_id} with progress for {new_date}")
