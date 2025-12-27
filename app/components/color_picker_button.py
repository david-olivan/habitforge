"""
Color Picker Button Component for HabitForge

A rounded button that displays the selected color and opens a color picker dialog.
"""

from kivymd.uix.button import MDRectangleFlatButton
from kivy.properties import StringProperty
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.logger import Logger


class ColorPickerButton(MDRectangleFlatButton):
    """
    Rounded button that displays selected color and opens picker dialog.

    Properties:
        selected_color: Currently selected color as hex string (e.g., "#E57373")
    """

    selected_color = StringProperty("#E57373")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(48)
        self._update_appearance()

    def on_selected_color(self, instance, value):
        """
        Update button appearance when color changes.

        Args:
            instance: This button instance
            value: New color hex code
        """
        self._update_appearance()
        Logger.info(f"ColorPickerButton: Color changed to {value}")

    def _update_appearance(self):
        """Set button color and text based on selected color."""
        # Set background color
        self.md_bg_color = get_color_from_hex(self.selected_color)

        # Display hex code as button text
        self.text = self.selected_color.upper()

        # Calculate luminance to determine contrasting text color
        rgb = get_color_from_hex(self.selected_color)
        luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]

        # Use black text on light colors, white on dark colors
        self.text_color = (0, 0, 0, 1) if luminance > 0.5 else (1, 1, 1, 1)

    def on_press(self):
        """Open color picker dialog when button is pressed."""
        from components.color_picker_dialog import ColorPickerDialog

        dialog = ColorPickerDialog(
            selected_color=self.selected_color,
            on_color_selected_callback=self._on_color_selected
        )
        dialog.open()
        Logger.info("ColorPickerButton: Opening color picker dialog")

    def _on_color_selected(self, color):
        """
        Handle color selection from dialog.

        Args:
            color: Selected color hex code
        """
        self.selected_color = color
