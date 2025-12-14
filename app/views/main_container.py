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

from views.main_screen import MainScreen
from views.analytics_content import AnalyticsContent
from views.account_content import AccountContent
from config.constants import BRAND_PRIMARY_RGB


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
            title="HabitForge",
            md_bg_color=BRAND_PRIMARY_RGB,  # Brand orange
            specific_text_color=(1, 1, 1, 1),  # White text
            elevation=0,
            size_hint_y=None,
            height=dp(56),
        )
        layout.add_widget(self.toolbar)

        # Bottom Navigation
        bottom_nav = MDBottomNavigation(
            panel_color=(1, 1, 1, 1),  # White background
            selected_color_background=(0.3, 0.6, 0.9, 0.15),  # Light blue tint
            text_color_active=(0.3, 0.6, 0.9, 1),  # Blue for active tab
        )

        # Habits Tab (existing MainScreen content)
        habits_tab = MDBottomNavigationItem(
            name="habits", text="Habits", icon="format-list-checkbox"
        )
        self.habits_screen = MainScreen(embedded=True)
        habits_tab.add_widget(self.habits_screen)

        # Manually trigger habit loading since on_enter won't fire for embedded screens
        self.habits_screen.load_habits()

        # Analytics Tab (placeholder)
        analytics_tab = MDBottomNavigationItem(
            name="analytics", text="Analytics", icon="chart-bar"
        )
        analytics_tab.add_widget(AnalyticsContent())

        # Account Tab (placeholder)
        account_tab = MDBottomNavigationItem(
            name="account", text="Account", icon="account-circle"
        )
        account_tab.add_widget(AccountContent())

        bottom_nav.add_widget(habits_tab)
        bottom_nav.add_widget(analytics_tab)
        bottom_nav.add_widget(account_tab)

        # Add bottom navigation to layout
        layout.add_widget(bottom_nav)

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
