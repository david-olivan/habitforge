"""
Color Picker Component for HabitForge

A reusable widget for selecting habit colors from a predefined palette.
"""

from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.properties import StringProperty, ListProperty, ColorProperty
from kivy.utils import get_color_from_hex
from kivy.logger import Logger
from config.constants import (
    HABIT_COLORS,
    DEFAULT_HABIT_COLOR,
    COLOR_PICKER_COLUMNS,
)


class ColorButton(Button):
    """
    A button representing a single color in the color picker.

    Shows the color as background and highlights when selected.
    """

    def __init__(self, color_hex: str, **kwargs):
        super().__init__(**kwargs)
        self.color_hex = color_hex
        self.size_hint = (None, None)
        self.size = ("60dp", "60dp")
        self.background_normal = ""  # Disable default background
        self.background_color = get_color_from_hex(color_hex)
        self.is_selected = False

    def set_selected(self, selected: bool):
        """
        Set the selected state of the button.

        Args:
            selected: True to mark as selected, False otherwise
        """
        self.is_selected = selected
        if selected:
            # Add visual indicator by slightly dimming the color
            base_color = get_color_from_hex(self.color_hex)
            self.background_color = [base_color[0], base_color[1], base_color[2], 0.8]
            # Could also add a checkmark icon here in future
        else:
            self.background_color = get_color_from_hex(self.color_hex)


class HabitColorPicker(GridLayout):
    """
    Grid of color buttons for selecting a habit color.

    Properties:
        selected_color: Currently selected color (hex string)
        colors: List of available colors
    """

    selected_color = StringProperty(DEFAULT_HABIT_COLOR)
    colors = ListProperty(HABIT_COLORS)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = COLOR_PICKER_COLUMNS
        self.spacing = "8dp"
        self.padding = "8dp"
        self.size_hint_y = None
        self.height = "140dp"  # Fixed height for 2 rows

        self.color_buttons = {}
        self._build_color_grid()

    def _build_color_grid(self):
        """
        Build the grid of color buttons.
        """
        self.clear_widgets()
        self.color_buttons = {}

        for color_hex in self.colors:
            btn = ColorButton(color_hex)
            btn.bind(on_press=lambda b, c=color_hex: self.on_color_selected(c))
            self.add_widget(btn)
            self.color_buttons[color_hex] = btn

        # Set initial selection
        if self.selected_color in self.color_buttons:
            self.color_buttons[self.selected_color].set_selected(True)

    def on_color_selected(self, color_hex: str):
        """
        Handle color selection.

        Args:
            color_hex: The selected color hex code
        """
        # Deselect all buttons
        for btn in self.color_buttons.values():
            btn.set_selected(False)

        # Select the clicked button
        if color_hex in self.color_buttons:
            self.color_buttons[color_hex].set_selected(True)
            self.selected_color = color_hex
            Logger.info(f"ColorPicker: Selected color {color_hex}")

    def set_color(self, color_hex: str):
        """
        Programmatically set the selected color.

        Args:
            color_hex: The color to select
        """
        if color_hex in self.color_buttons:
            self.on_color_selected(color_hex)
        else:
            Logger.warning(f"ColorPicker: Color {color_hex} not in palette")

    def on_selected_color(self, instance, value):
        """
        Called when selected_color property changes.
        Updates UI to reflect the new selection.
        """
        Logger.info(f"ColorPicker: selected_color changed to {value}")
