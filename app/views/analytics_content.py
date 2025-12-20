"""
Analytics Content for HabitForge

Calendar heatmap visualization showing habit completion patterns over time.
GitHub-style heatmap with color intensity based on completion percentage.
"""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.gridlayout import MDGridLayout
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from datetime import date
from typing import Optional
from dateutil.relativedelta import relativedelta

from models.database import get_all_habits
from components.heatmap_grid import HeatmapGrid
from logic.heatmap_data import get_heatmap_data, calculate_overall_percentage
from logic.date_utils import get_today
from config.constants import BRAND_PRIMARY_RGB, hex_to_rgba
from kivy.logger import Logger


class HeatmapViewTab(MDBoxLayout, MDTabsBase):
    """Base class for view tab content (Week/Month/Year)."""
    pass


class DateNavigationBar(MDBoxLayout):
    """
    Navigation bar with Previous/Today/Next buttons and date label.
    """

    date_label_text = StringProperty("Loading...")  # Displayed date range
    on_previous = ObjectProperty(None)  # Callback for previous button
    on_next = ObjectProperty(None)  # Callback for next button
    on_today = ObjectProperty(None)  # Callback for today button

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = dp(8)
        self.padding = dp(16)
        self.size_hint_y = None
        self.height = dp(56)

        # Previous button
        self.prev_btn = MDIconButton(
            icon="chevron-left",
            on_release=self._on_prev_clicked,
            pos_hint={"center_y": 0.5}
        )
        self.add_widget(self.prev_btn)

        # Date label (centered, takes remaining space)
        self.date_label = MDLabel(
            text=self.date_label_text,
            halign="center",
            valign="middle",
            theme_text_color="Primary",
            font_style="Subtitle1"
        )
        self.bind(date_label_text=lambda _, text: setattr(self.date_label, 'text', text))
        self.add_widget(self.date_label)

        # Today button - REMOVED per user request
        # self.today_btn = MDFlatButton(
        #     text="Today",
        #     on_release=self._on_today_clicked
        # )
        # self.add_widget(self.today_btn)

        # Next button
        self.next_btn = MDIconButton(
            icon="chevron-right",
            on_release=self._on_next_clicked,
            pos_hint={"center_y": 0.5}
        )
        self.add_widget(self.next_btn)

    def _on_prev_clicked(self, instance):
        """Trigger previous callback."""
        if self.on_previous:
            self.on_previous()

    def _on_next_clicked(self, instance):
        """Trigger next callback."""
        if self.on_next:
            self.on_next()

    def _on_today_clicked(self, instance):
        """Trigger today callback."""
        if self.on_today:
            self.on_today()


class HabitHeatmapCard(MDCard):
    """
    Card displaying a heatmap for a single habit.

    Shows habit name, overall completion percentage, and heatmap grid.
    """

    def __init__(self, habit: dict, view_type: str, reference_date: date, **kwargs):
        super().__init__(**kwargs)

        # Store parameters
        self.habit = habit  # {id, name, color, goal_count, goal_type}
        self.view_type = view_type
        self.reference_date = reference_date

        # Card styling
        self.orientation = "vertical"
        self.size_hint_y = None
        self.size_hint_x = None
        self.width = dp(180)  # Fixed width to fit 2 per row
        self.height = dp(200)  # Will adjust based on content
        self.padding = dp(6)
        self.spacing = dp(4)
        self.elevation = 0.25
        self.radius = dp(8)

        # Build UI
        self._build_ui()

        # Load data
        Clock.schedule_once(lambda dt: self.load_heatmap_data(), 0.1)

    def _build_ui(self):
        """Build card UI components."""
        # Header layout (horizontal)
        header = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(4),
            size_hint_y=None,
            height=dp(24)
        )

        # Habit name with color indicator
        habit_name_container = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(4),
            size_hint_x=0.7
        )

        # Color indicator (small colored square using MDIcon)
        from kivymd.uix.label import MDIcon
        color_indicator = MDIcon(
            icon="square-rounded",
            theme_text_color="Custom",
            text_color=hex_to_rgba(self.habit['color']),
            size_hint_x=None,
            width=dp(16)
        )
        habit_name_container.add_widget(color_indicator)

        # Habit name
        habit_name = MDLabel(
            text=self.habit['name'],
            theme_text_color="Primary",
            font_style="Caption",
            bold=True
        )
        habit_name_container.add_widget(habit_name)

        header.add_widget(habit_name_container)

        # Completion percentage (right-aligned)
        self.percentage_label = MDLabel(
            text="0%",
            theme_text_color="Secondary",
            font_style="Caption",
            font_size="9sp",
            halign="right",
            size_hint_x=0.3
        )
        header.add_widget(self.percentage_label)

        self.add_widget(header)

        # Heatmap grid
        self.heatmap_grid = HeatmapGrid()
        self.add_widget(self.heatmap_grid)

    def load_heatmap_data(self):
        """Fetch completion data and populate heatmap grid."""
        try:
            # Calculate date range for view type
            cols, rows, start_date, end_date = HeatmapGrid.calculate_grid_dimensions(
                self.view_type, self.reference_date
            )

            # Configure grid
            self.heatmap_grid.cols = cols

            # Fetch heatmap data (with caching)
            completion_data = get_heatmap_data(
                habit_id=self.habit['id'],
                start_date=start_date,
                end_date=end_date,
                view_type=self.view_type,
                reference_date=self.reference_date,
                use_cache=True
            )

            # Calculate overall percentage for header
            overall_percentage = calculate_overall_percentage(
                completion_data,
                self.habit['goal_count'],
                start_date,
                end_date
            )

            # Update header label
            self.percentage_label.text = f"{overall_percentage:.0f}%"

            # Populate grid with cells
            self.heatmap_grid.populate_grid(
                start_date=start_date,
                end_date=end_date,
                completion_data=completion_data,
                habit_color=self.habit['color'],
                goal_count=self.habit['goal_count'],
                goal_type=self.habit['goal_type']
            )

            # Adjust card height based on grid
            header_height = dp(24)
            spacing = dp(4) * 2  # Top and bottom spacing
            padding = dp(6) * 2  # Top and bottom padding

            # Ensure heatmap_grid.height is a scalar value
            grid_height = self.heatmap_grid.height
            if isinstance(grid_height, (list, tuple)):
                grid_height = grid_height[0] if grid_height else 0

            self.height = header_height + grid_height + spacing + padding

            Logger.info(
                f"HabitHeatmapCard: Loaded heatmap for '{self.habit['name']}' - {overall_percentage:.0f}%"
            )

        except Exception as e:
            import traceback
            Logger.error(f"HabitHeatmapCard: Failed to load heatmap: {e}")
            Logger.error(f"HabitHeatmapCard: Traceback: {traceback.format_exc()}")
            # Show error state
            self.percentage_label.text = "Error"

    def update_view(self, view_type: str, reference_date: date):
        """
        Update card with new view type or reference date.

        Args:
            view_type: "week", "month", or "year"
            reference_date: New reference date
        """
        self.view_type = view_type
        self.reference_date = reference_date
        self.load_heatmap_data()


class AnalyticsContent(MDBoxLayout):
    """
    Main analytics screen with calendar heatmap visualization.

    Shows GitHub-style heatmaps for all active habits with view switcher
    (Week/Month/Year) and date navigation.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # State
        self.current_view = "month"  # Default view
        self.reference_date = get_today()
        self.habit_cards = []  # List of HabitHeatmapCard widgets

        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build the main analytics UI."""
        # View switcher (Week/Month/Year tabs) - COMMENTED OUT Week/Year per user request
        # Create MDTabs without height first to avoid initialization issues
        # self.tabs = MDTabs()

        # Add tabs - Only Month view enabled
        # self.tabs.add_widget(HeatmapViewTab(title="Week"))
        # self.tabs.add_widget(HeatmapViewTab(title="Month"))
        # self.tabs.add_widget(HeatmapViewTab(title="Year"))

        # Set size after tabs are added
        # self.tabs.size_hint_y = None
        # self.tabs.height = dp(48)

        # Bind tab switch event after adding widgets
        # self.tabs.bind(on_tab_switch=self._on_view_switched)

        # self.add_widget(self.tabs)

        # Date navigation bar
        self.nav_bar = DateNavigationBar()
        self.nav_bar.on_previous = self._navigate_previous
        self.nav_bar.on_next = self._navigate_next
        self.nav_bar.on_today = self._navigate_today
        self.add_widget(self.nav_bar)

        # Update date label
        self._update_date_label()

        # Scrollable content area
        scroll = MDScrollView(size_hint=(1, 1))
        self.heatmaps_container = MDGridLayout(
            cols=2,  # 2 cards per row
            spacing=dp(8),
            padding=dp(8),
            size_hint_y=None
        )
        self.heatmaps_container.bind(
            minimum_height=self.heatmaps_container.setter("height")
        )

        scroll.add_widget(self.heatmaps_container)
        self.add_widget(scroll)

        # Load habits when screen is ready
        Clock.schedule_once(lambda dt: self.load_habits(), 0.2)

    def load_habits(self):
        """Load all active habits and create heatmap cards."""
        try:
            # Clear existing cards
            self.heatmaps_container.clear_widgets()
            self.habit_cards = []

            # Get all active habits
            habits = get_all_habits(include_archived=False)

            if not habits:
                # Show empty state
                self._show_empty_state()
                return

            # Create heatmap card for each habit
            for habit in habits:
                card = HabitHeatmapCard(
                    habit={
                        'id': habit.id,
                        'name': habit.name,
                        'color': habit.color,
                        'goal_count': habit.goal_count,
                        'goal_type': habit.goal_type
                    },
                    view_type=self.current_view,
                    reference_date=self.reference_date
                )

                self.heatmaps_container.add_widget(card)
                self.habit_cards.append(card)

            Logger.info(f"AnalyticsContent: Loaded {len(habits)} habit heatmaps")

        except Exception as e:
            Logger.error(f"AnalyticsContent: Failed to load habits: {e}")

    def _show_empty_state(self):
        """Display message when no habits exist."""
        empty_label = MDLabel(
            text="No habits yet\n\nCreate a habit to see analytics",
            halign="center",
            theme_text_color="Secondary",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(100)
        )
        self.heatmaps_container.add_widget(empty_label)

    def _on_view_switched(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        """Handle view tab switch (Week/Month/Year)."""
        self.current_view = tab_text.lower()
        self._update_date_label()
        self._reload_all_heatmaps()

        Logger.info(f"AnalyticsContent: Switched to {tab_text} view")

    def _navigate_previous(self):
        """Navigate to previous period."""
        if self.current_view == "week":
            self.reference_date -= relativedelta(weeks=1)
        elif self.current_view == "month":
            self.reference_date -= relativedelta(months=1)
        elif self.current_view == "year":
            self.reference_date -= relativedelta(years=1)

        self._update_date_label()
        self._reload_all_heatmaps()

    def _navigate_next(self):
        """Navigate to next period."""
        if self.current_view == "week":
            self.reference_date += relativedelta(weeks=1)
        elif self.current_view == "month":
            self.reference_date += relativedelta(months=1)
        elif self.current_view == "year":
            self.reference_date += relativedelta(years=1)

        self._update_date_label()
        self._reload_all_heatmaps()

    def _navigate_today(self):
        """Navigate to current date."""
        self.reference_date = get_today()
        self._update_date_label()
        self._reload_all_heatmaps()

    def _update_date_label(self):
        """Update navigation bar date label based on current view."""
        if self.current_view == "week":
            # Calculate week start and end
            days_since_monday = self.reference_date.weekday()
            week_start = self.reference_date - relativedelta(days=days_since_monday)
            week_end = week_start + relativedelta(days=6)
            self.nav_bar.date_label_text = (
                f"Week of {week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}"
            )

        elif self.current_view == "month":
            self.nav_bar.date_label_text = self.reference_date.strftime("%B %Y")

        elif self.current_view == "year":
            self.nav_bar.date_label_text = str(self.reference_date.year)

    def _reload_all_heatmaps(self):
        """Reload data for all visible heatmap cards."""
        for card in self.habit_cards:
            card.update_view(self.current_view, self.reference_date)

        Logger.debug(f"AnalyticsContent: Reloaded {len(self.habit_cards)} heatmaps")

    def refresh_on_tab_enter(self):
        """
        Refresh analytics when user switches to this tab.

        Call this from main_container.py when Analytics tab is selected.
        """
        Logger.info("AnalyticsContent: Refreshing on tab enter")
        self.load_habits()
