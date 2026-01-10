"""
Main Container Screen for HabitForge

Container screen with bottom navigation tabs and shared top app bar.
Implements Material Design 3 navigation pattern.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.clock import Clock

from views.main_screen import MainScreen
from views.analytics_content import AnalyticsContent
from views.account_content import AccountContent
from config.constants import BRAND_PRIMARY_RGB
from logic.localization import _


class MainContainerScreen(MDScreen):
    """
    Container screen with bottom navigation tabs.

    Features:
    - Shared top app bar with logo across all tabs
    - Bottom navigation with 3 tabs: Habits, Analytics, Account
    - Material Design 3 styling
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main_container"

        # Swipe gesture state
        self.swipe_start_x = None
        self.swipe_start_y = None
        self.swipe_in_progress = False

        self.build_ui()

    def build_ui(self):
        """Build the container UI with bottom navigation."""
        # Main layout
        layout = MDBoxLayout(orientation="vertical")

        # Top safe area (5% of screen height for status bar)
        top_padding_height = Window.height * 0.05
        top_safe_area = MDBoxLayout(
            size_hint_y=None,
            height=top_padding_height,
            md_bg_color=BRAND_PRIMARY_RGB,  # Match toolbar color
        )
        layout.add_widget(top_safe_area)

        # App title bar (no logo, just title)
        self.toolbar = MDTopAppBar(
            title=_("app_name"),
            md_bg_color=BRAND_PRIMARY_RGB,  # Brand orange
            specific_text_color=(1, 1, 1, 1),  # White text
            elevation=0,
            size_hint_y=None,
            height=dp(56),
        )
        layout.add_widget(self.toolbar)

        # Bottom Navigation
        self.bottom_nav = MDBottomNavigation(
            panel_color=(1, 1, 1, 1),  # White background
            selected_color_background=(0.3, 0.6, 0.9, 0.15),  # Light blue tint
            text_color_active=(0.3, 0.6, 0.9, 1),  # Blue for active tab
        )

        # Habits Tab (existing MainScreen content)
        self.habits_tab = MDBottomNavigationItem(
            name="habits", text=_("tabs.habits"), icon="format-list-checkbox"
        )
        self.habits_screen = MainScreen(embedded=True)
        self.habits_tab.add_widget(self.habits_screen)

        # Manually trigger habit loading since on_enter won't fire for embedded screens
        self.habits_screen.load_habits()

        # Analytics Tab (placeholder)
        self.analytics_tab = MDBottomNavigationItem(
            name="analytics", text=_("tabs.analytics"), icon="chart-bar"
        )
        self.analytics_content = AnalyticsContent()
        self.analytics_tab.add_widget(self.analytics_content)

        # Account Tab (placeholder)
        self.account_tab = MDBottomNavigationItem(
            name="account", text=_("tabs.account"), icon="account-circle"
        )
        self.account_content = AccountContent()
        self.account_tab.add_widget(self.account_content)

        self.bottom_nav.add_widget(self.habits_tab)
        self.bottom_nav.add_widget(self.analytics_tab)
        self.bottom_nav.add_widget(self.account_tab)

        # Bind to tab switch event to refresh analytics when user navigates to it
        self.bottom_nav.bind(on_switch_tabs=self._on_tab_switch)
        Logger.info(f"MainContainer: Bound to on_switch_tabs event. Initial tab: {self.bottom_nav.current}")

        # Add bottom navigation to layout
        layout.add_widget(self.bottom_nav)

        # Bottom safe area (5% of screen height for navigation gesture bar)
        bottom_padding_height = Window.height * 0.05
        bottom_safe_area = MDBoxLayout(
            size_hint_y=None,
            height=bottom_padding_height,
            md_bg_color=(1, 1, 1, 1),  # Match bottom nav background (white)
        )
        layout.add_widget(bottom_safe_area)

        # Assemble layout
        self.add_widget(layout)

    def on_touch_down(self, touch):
        """Capture swipe start position."""
        self.swipe_start_x = touch.x
        self.swipe_start_y = touch.y
        self.swipe_in_progress = True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        """Detect swipe gesture on release."""
        if not self.swipe_in_progress:
            return super().on_touch_up(touch)

        # Calculate swipe delta
        dx = touch.x - self.swipe_start_x
        dy = touch.y - self.swipe_start_y

        # Reset state
        self.swipe_in_progress = False

        # Swipe detection thresholds
        MIN_SWIPE_DISTANCE = 100  # pixels (~25% of typical screen width)
        MAX_VERTICAL_DEVIATION = 80  # pixels (distinguish from vertical scrolling)

        # Check if horizontal swipe (not vertical scroll)
        if abs(dx) > MIN_SWIPE_DISTANCE and abs(dy) < MAX_VERTICAL_DEVIATION:
            current_tab = self.bottom_nav.current

            # Swipe left: Habits -> Analytics
            if dx < 0 and current_tab == "habits":
                self.bottom_nav.switch_tab("analytics")
                return True

            # Swipe right: Analytics -> Habits
            elif dx > 0 and current_tab == "analytics":
                self.bottom_nav.switch_tab("habits")
                return True

        return super().on_touch_up(touch)

    def _on_tab_switch(self, instance_bottom_nav, instance_bottom_nav_item, name_tab):
        """
        Handle tab switch events to refresh data when needed.

        Called by MDBottomNavigation.on_switch_tabs event.

        Args:
            instance_bottom_nav: The MDBottomNavigation instance
            instance_bottom_nav_item: The MDBottomNavigationItem being switched to
            name_tab: The name of the newly selected tab
        """
        Logger.info(f"MainContainer: Tab switched to '{name_tab}'")

        if name_tab == "analytics":
            # Refresh analytics data when user switches to Analytics tab
            # Only actually refreshes if cache has been invalidated
            self.analytics_content.refresh_on_tab_enter()
