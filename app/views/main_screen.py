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
from kivymd.uix.button import MDFloatingActionButton
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import date

from app.models.database import get_all_habits
from app.logic.completion_manager import log_completion, get_habit_progress
from app.components.habit_card import HabitCard
from config.constants import GOAL_TYPE_LABELS
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main_screen"

        # Data storage
        self.habits = []
        self.daily_habits = []
        self.weekly_habits = []
        self.monthly_habits = []
        self.progress_data = {}
        self.habit_cards = {}  # Map habit_id to HabitCard widget

        # Build UI
        self.build_ui()

    def build_ui(self):
        """Build the main screen UI."""
        # Main container
        main_layout = MDBoxLayout(orientation="vertical")

        # Top app bar
        self.toolbar = MDTopAppBar(
            title="HabitForge",
            md_bg_color=(0.3, 0.6, 0.9, 1),  # Blue
            specific_text_color=(1, 1, 1, 1),  # White text
        )

        # Scrollable content area
        scroll = MDScrollView()
        self.content_layout = MDBoxLayout(
            orientation="vertical", spacing=dp(16), padding=dp(16), size_hint_y=None
        )
        self.content_layout.bind(
            minimum_height=self.content_layout.setter("height")
        )  # Make scrollable

        # Date header
        self.date_label = MDLabel(
            text=self._format_today(),
            font_style="Subtitle1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(32),
        )
        self.content_layout.add_widget(self.date_label)

        # Placeholder for habit sections (will be populated in on_enter)
        self.sections_container = MDBoxLayout(
            orientation="vertical", spacing=dp(24), size_hint_y=None
        )
        self.sections_container.bind(
            minimum_height=self.sections_container.setter("height")
        )
        self.content_layout.add_widget(self.sections_container)

        scroll.add_widget(self.content_layout)

        # FAB button (Add Habit)
        self.fab = MDFloatingActionButton(
            icon="plus",
            md_bg_color=(0.3, 0.6, 0.9, 1),  # Blue
            pos_hint={"center_x": 0.9, "center_y": 0.1},
            on_release=self.navigate_to_add_habit,
        )

        # Assemble layout
        main_layout.add_widget(self.toolbar)
        main_layout.add_widget(scroll)
        main_layout.add_widget(self.fab)

        self.add_widget(main_layout)

    def _format_today(self) -> str:
        """Format today's date as 'Day, Month Date'."""
        today = date.today()
        return today.strftime("Today: %A, %b %d")

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

        Logger.info(
            f"MainScreen: Loaded {len(self.habits)} habits "
            f"(daily={len(self.daily_habits)}, weekly={len(self.weekly_habits)}, monthly={len(self.monthly_habits)})"
        )

        # Load progress for all habits
        self.load_progress_data()

        # Render the UI
        self.render_habit_sections()

    def load_progress_data(self):
        """Calculate progress for all habits."""
        for habit in self.habits:
            progress = get_habit_progress(
                habit.id, habit.goal_count, habit.goal_type
            )
            self.progress_data[habit.id] = progress
            Logger.debug(
                f"MainScreen: Progress for '{habit.name}': {progress['current_count']}/{progress['goal_count']}"
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
            self.render_section("Daily Goals", self.daily_habits)

        # Render Weekly section
        if self.weekly_habits:
            self.render_section("Weekly Goals", self.weekly_habits)

        # Render Monthly section
        if self.monthly_habits:
            self.render_section("Monthly Goals", self.monthly_habits)

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

        # Section header
        header = MDLabel(
            text=f"{title} ({len(habits)})",
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(32),
        )
        section.add_widget(header)

        # Habit cards
        for habit in habits:
            habit_dict = {
                "id": habit.id,
                "name": habit.name,
                "color": habit.color,
                "goal_type": habit.goal_type,
                "goal_count": habit.goal_count,
            }
            progress_dict = self.progress_data.get(habit.id, {})

            card = HabitCard(
                habit=habit_dict, progress=progress_dict, on_increment=self.on_increment
            )
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

        Args:
            habit_id: The ID of the habit to increment
        """
        Logger.info(f"MainScreen: Increment requested for habit ID {habit_id}")

        # Log the completion
        success, error, completion = log_completion(habit_id)

        if success:
            Logger.info(f"MainScreen: Completion logged successfully")
            # Refresh progress for this habit
            self.refresh_habit_progress(habit_id)
        else:
            Logger.error(f"MainScreen: Failed to log completion: {error}")
            self.show_error(error or "Failed to log completion")

    def refresh_habit_progress(self, habit_id: int):
        """
        Reload progress for a single habit and update its card.

        Args:
            habit_id: The ID of the habit to refresh
        """
        # Find the habit
        habit = next((h for h in self.habits if h.id == habit_id), None)
        if not habit:
            Logger.warning(f"MainScreen: Habit ID {habit_id} not found for refresh")
            return

        # Recalculate progress
        progress = get_habit_progress(habit.id, habit.goal_count, habit.goal_type)
        self.progress_data[habit_id] = progress

        # Update the card
        card = self.habit_cards.get(habit_id)
        if card:
            card.progress = progress
            Logger.debug(
                f"MainScreen: Updated card for habit '{habit.name}' with new progress"
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

    def navigate_to_add_habit(self, button):
        """Navigate to the habit form screen to add a new habit."""
        Logger.info("MainScreen: Navigating to habit form")
        if self.manager:
            self.manager.current = "habit_form"

    def refresh_on_return(self):
        """
        Refresh the habit list when returning from another screen.

        Call this method when navigating back to ensure the list is up-to-date.
        """
        Logger.info("MainScreen: Refreshing habits after return")
        self.load_habits()
