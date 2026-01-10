"""
Color Picker Dialog Component for HabitForge

A dialog wrapper around the HabitColorPicker component for color selection.
"""

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from components.color_picker import HabitColorPicker
from kivy.logger import Logger


class ColorPickerDialog:
    """
    Dialog wrapper for HabitColorPicker component.

    Displays the color picker grid in a popup dialog that auto-dismisses
    when a color is selected.

    Args:
        selected_color: Initially selected color hex code
        on_color_selected_callback: Function to call when color is selected
    """

    def __init__(self, selected_color, on_color_selected_callback):
        self.callback = on_color_selected_callback

        # Create color picker widget
        self.picker = HabitColorPicker(selected_color=selected_color)
        self.picker.bind(selected_color=self._on_color_picked)

        # Create dialog with color picker as content
        self.dialog = MDDialog(
            title="Choose Color",
            type="custom",
            content_cls=self.picker,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )

    def _on_color_picked(self, instance, color):
        """
        Handle color selection from picker.

        Args:
            instance: The HabitColorPicker instance
            color: Selected color hex code
        """
        Logger.info(f"ColorPickerDialog: Color selected: {color}")
        self.callback(color)
        self.dialog.dismiss()

    def open(self):
        """Open the color picker dialog."""
        self.dialog.open()
        Logger.info("ColorPickerDialog: Dialog opened")
