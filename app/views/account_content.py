"""
Account Content for HabitForge

Placeholder screen for account settings and preferences.
Will be implemented in future phases.
"""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.metrics import dp


class AccountContent(MDBoxLayout):
    """
    Placeholder content for Account tab.

    Future implementation will include:
    - App settings
    - Data export/backup
    - Theme preferences
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(32)
        self.spacing = dp(16)

        # Placeholder text
        placeholder = MDLabel(
            text="Account Settings Coming Soon\n\nHabitForge v1.0",
            halign="center",
            theme_text_color="Secondary",
            font_style="Subtitle1",
        )
        self.add_widget(placeholder)
