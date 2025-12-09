"""
Analytics Content for HabitForge

Placeholder screen for analytics and progress visualization.
Will be implemented in PRD Section 2.2 (Phase 2).
"""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.metrics import dp


class AnalyticsContent(MDBoxLayout):
    """
    Placeholder content for Analytics tab.

    Future implementation will include:
    - Streak tracking
    - Calendar heatmap visualization
    - Progress statistics
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(32)
        self.spacing = dp(16)

        # Placeholder text
        placeholder = MDLabel(
            text="Analytics Coming Soon\n\nTrack your progress with visual insights",
            halign="center",
            theme_text_color="Secondary",
            font_style="Subtitle1",
        )
        self.add_widget(placeholder)
