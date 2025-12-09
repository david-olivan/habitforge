"""
Main Container Screen for HabitForge

Container screen with bottom navigation tabs and shared top app bar.
Implements Material Design 3 navigation pattern.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.image import Image
from kivy.metrics import dp

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

        # Top App Bar with logo
        toolbar_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            md_bg_color=BRAND_PRIMARY_RGB,  # Brand orange from logo
            padding=[dp(16), 0, dp(16), 0],
        )

        # Logo icon with shadow effect
        logo_container = MDBoxLayout(
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            pos_hint={"center_y": 0.5},
        )

        # Add shadow using canvas instructions
        from kivy.graphics import Color, Ellipse
        with logo_container.canvas.before:
            Color(0, 0, 0, 0.3)  # Semi-transparent black shadow
            self.logo_shadow = Ellipse(
                pos=(logo_container.x + dp(1), logo_container.y - dp(1)),
                size=(dp(36), dp(36))
            )

        logo = Image(
            source="assets/icons/habitforge-icon-48.png",
            size_hint=(None, None),
            size=(dp(32), dp(32)),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        logo_container.add_widget(logo)

        # Bind to update shadow position when layout changes
        def update_shadow(*args):
            self.logo_shadow.pos = (logo_container.x + dp(1), logo_container.y - dp(1))
            self.logo_shadow.size = (dp(36), dp(36))
        logo_container.bind(pos=update_shadow, size=update_shadow)

        toolbar_layout.add_widget(logo_container)

        # App title
        self.toolbar = MDTopAppBar(
            title="HabitForge",
            md_bg_color=BRAND_PRIMARY_RGB,  # Same brand orange
            specific_text_color=(1, 1, 1, 1),  # White text
            elevation=0,
        )
        toolbar_layout.add_widget(self.toolbar)

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

        # Assemble layout
        layout.add_widget(toolbar_layout)
        layout.add_widget(bottom_nav)
        self.add_widget(layout)
