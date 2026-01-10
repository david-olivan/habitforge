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
from views.import_data_screen import ImportDataScreen
from views.delete_data_screen import DeleteDataScreen


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
        # Set window size for desktop testing only
        from kivy.utils import platform
        if platform not in ('android', 'ios'):
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

        # Load language preference from database
        try:
            from logic.localization import load_language_from_database
            load_language_from_database()
            Logger.info("HabitForge: Language preference loaded successfully")
        except Exception as e:
            Logger.error(f"HabitForge: Failed to load language preference: {e}")

        # Create screen manager
        screen_manager = MDScreenManager()

        # Add screens
        main_container = MainContainerScreen()
        Logger.info(f"HabitForge: Adding MainContainerScreen with name='{main_container.name}'")
        screen_manager.add_widget(main_container)

        habit_form = HabitFormScreen()
        Logger.info(f"HabitForge: Adding HabitFormScreen with name='{habit_form.name}'")
        screen_manager.add_widget(habit_form)

        import_screen = ImportDataScreen()
        Logger.info(f"HabitForge: Adding ImportDataScreen with name='{import_screen.name}'")
        screen_manager.add_widget(import_screen)

        delete_screen = DeleteDataScreen()
        Logger.info(f"HabitForge: Adding DeleteDataScreen with name='{delete_screen.name}'")
        screen_manager.add_widget(delete_screen)

        # Log all registered screen names
        Logger.info(f"HabitForge: All registered screens: {screen_manager.screen_names}")

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