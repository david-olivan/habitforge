"""
HabitForge - Personal Habit Tracker

Main application entry point.
"""

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.core.window import Window
from kivy.logger import Logger

from models.database import init_database
from views.habit_form import HabitFormScreen
from views.main_container import MainContainerScreen


class HabitForgeApp(MDApp):
    """
    Main application class for HabitForge.
    """

    def build(self):
        """
        Build and return the root widget.

        Returns:
            Widget: Root widget (ScreenManager with MainScreen and HabitFormScreen)
        """
        # Set window size for desktop testing
        Window.size = (400, 700)

        # Set app theme
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.material_style = "M3"  # Material Design 3

        # Initialize database
        try:
            init_database()
            Logger.info("HabitForge: Database initialized successfully")
        except Exception as e:
            Logger.error(f"HabitForge: Failed to initialize database: {e}")

        # Create screen manager
        screen_manager = MDScreenManager()

        # Add screens
        screen_manager.add_widget(MainContainerScreen())
        screen_manager.add_widget(HabitFormScreen())

        # Set default screen to main_container
        screen_manager.current = "main_container"

        return screen_manager

    def on_start(self):
        """
        Called when the application starts.
        """
        Logger.info("HabitForge: Application started")


if __name__ == "__main__":
    HabitForgeApp().run()