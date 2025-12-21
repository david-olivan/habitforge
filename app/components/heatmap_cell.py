"""
Heatmap Cell Component for HabitForge

Individual cell widget for the calendar heatmap visualization.
Displays completion intensity using color-coded rectangles.
"""

from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp
from config.constants import hex_to_rgba, BRAND_PRIMARY_RGB


class HeatmapCell(Widget):
    """
    A single cell in the heatmap grid.

    Displays a colored square representing completion percentage for a specific date.
    Color intensity increases with completion percentage:
    - 0%: Light grey
    - 1-49%: Light shade of habit color
    - 50-99%: Medium shade of habit color
    - 100%+: Full habit color
    """

    # Properties
    cell_date = ObjectProperty(None)  # date object for this cell
    completion_percentage = NumericProperty(0.0)  # 0-100+
    habit_color = StringProperty("#E57373")  # Hex color (default red)
    is_today = BooleanProperty(False)  # Highlight current date
    # is_future = BooleanProperty(False)  # REMOVED: All dates shown as grey initially

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set default size
        self.size_hint = (None, None)
        self.size = (dp(20), dp(20))

        # Bind property changes to redraw
        self.bind(
            completion_percentage=self._update_canvas,
            habit_color=self._update_canvas,
            is_today=self._update_canvas,
            pos=self._update_canvas,
            size=self._update_canvas
        )

        # Initial draw
        self._update_canvas()

    def _update_canvas(self, *args):
        """Redraw the cell when properties change."""
        self.canvas.clear()

        with self.canvas:
            # Draw background rectangle with completion color
            color = self._get_cell_color()
            Color(*color)
            Rectangle(pos=self.pos, size=self.size)

            # Draw border for today's date
            if self.is_today:
                Color(*BRAND_PRIMARY_RGB)  # Orange border
                Line(rectangle=(self.x, self.y, self.width, self.height), width=2)

    def _get_cell_color(self):
        """
        Calculate cell color based on completion percentage.

        Uses opacity/alpha blending where percentage directly maps to opacity.
        0% = grey, 1-100% = increasing opacity of habit color.

        Returns:
            tuple: RGBA color tuple (r, g, b, a) with values 0.0-1.0
        """
        # No completion - light grey (all dates start grey)
        if self.completion_percentage <= 0:
            return (0.95, 0.95, 0.95, 1)  # Light grey

        # Parse habit color to RGB
        base_r, base_g, base_b = self._hex_to_rgb(self.habit_color)

        # Map percentage (0-100) directly to opacity (0.0-1.0)
        # Percentage represents how much of the goal is complete
        alpha = min(1.0, self.completion_percentage / 100.0)

        # Blend with white background based on alpha
        final_r = base_r * alpha + 1.0 * (1 - alpha)
        final_g = base_g * alpha + 1.0 * (1 - alpha)
        final_b = base_b * alpha + 1.0 * (1 - alpha)

        return (final_r, final_g, final_b, 1.0)

    @staticmethod
    def _hex_to_rgb(hex_color):
        """
        Convert hex color to RGB tuple (0.0-1.0 range).

        Args:
            hex_color: Hex color string (e.g., "#E57373")

        Returns:
            tuple: (r, g, b) with values 0.0-1.0
        """
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)
