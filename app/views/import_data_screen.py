"""
Import Data Screen for HabitForge

Full-screen view for importing backup data with file picker and warnings.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.clock import Clock

from logic.data_manager import get_data_counts, import_from_csv
from logic.localization import _
from config.constants import IMPORT_BUTTON_COLOR, BRAND_PRIMARY_RGB


class ImportDataScreen(MDScreen):
    """
    Screen for importing backup data.

    Shows warnings about data replacement, allows file selection,
    and executes import operation.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "import_data"

        # State
        self.selected_file = None
        self.data_counts = {"habit_count": 0, "completion_count": 0}
        self.is_importing = False

        # Store callback to prevent garbage collection
        self._file_picker_callback = None

        # Build UI
        self._build_ui()

        Logger.info(f"ImportDataScreen: Initialized with name='{self.name}'")

    def on_pre_enter(self):
        """Reset state before screen appears."""
        Logger.info("ImportDataScreen: Entering screen")
        self.selected_file = None
        self.is_importing = False
        self._load_data_counts()
        self._update_button_state()
        self._update_file_display()

    def _build_ui(self):
        """Build the screen user interface."""
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

        # App title bar with back button
        toolbar = MDTopAppBar(
            title=_("screens.import_data.title"),
            md_bg_color=BRAND_PRIMARY_RGB,  # Brand orange
            specific_text_color=(1, 1, 1, 1),  # White text
            elevation=0,
            size_hint_y=None,
            height=dp(56),
            left_action_items=[["arrow-left", lambda x: self._on_cancel()]],
        )
        layout.add_widget(toolbar)

        # Content container with padding
        bottom_padding = Window.height * 0.05
        container = MDBoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(16), dp(20), bottom_padding],
            spacing=dp(16)
        )

        # Warning Card
        warning_card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(180),
            md_bg_color=(1, 0.95, 0.8, 1),  # Light orange warning color
        )

        # Warning title with icon
        warning_title_container = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(32),
        )

        warning_icon = MDIconButton(
            icon="alert",
            icon_size="24sp",
            theme_text_color="Custom",
            text_color=(0.9, 0.6, 0.2, 1),  # Orange warning color
            disabled=True,  # Not clickable, just for display
            size_hint=(None, None),
            size=(dp(32), dp(32)),
        )
        warning_title_container.add_widget(warning_icon)

        warning_title = MDLabel(
            text=_("screens.import_data.warning_title"),
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=(0.9, 0.6, 0.2, 1),  # Orange warning color
            valign="middle",
        )
        warning_title_container.add_widget(warning_title)
        warning_card.add_widget(warning_title_container)

        # Warning message
        warning_message = MDLabel(
            text=_("screens.import_data.warning_message"),
            font_style="Body1",
            size_hint_y=None,
            height=dp(24),
        )
        warning_card.add_widget(warning_message)

        # Data counts label
        self.data_counts_label = MDLabel(
            text="",
            font_style="Body2",
            size_hint_y=None,
            height=dp(24),
        )
        warning_card.add_widget(self.data_counts_label)

        # Subtitle
        subtitle = MDLabel(
            text=_("screens.import_data.subtitle"),
            font_style="Caption",
            size_hint_y=None,
            height=dp(24),
        )
        warning_card.add_widget(subtitle)

        container.add_widget(warning_card)

        # Choose File Button
        choose_file_btn = MDRaisedButton(
            text=_("screens.import_data.choose_file"),
            size_hint_x=1,
            size_hint_y=None,
            height=dp(48),
            on_release=self._on_choose_file,
        )
        container.add_widget(choose_file_btn)

        # Selected file display
        self.file_display_label = MDLabel(
            text=_("screens.import_data.no_file"),
            font_style="Caption",
            size_hint_y=None,
            height=dp(24),
            halign="center",
        )
        container.add_widget(self.file_display_label)

        # Progress spinner (hidden initially)
        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={'center_x': 0.5},
            active=False,
        )
        container.add_widget(self.spinner)

        # Spacer to push buttons to bottom
        container.add_widget(MDLabel())

        # Error/Success message display
        self.message_label = MDLabel(
            text="",
            theme_text_color="Custom",
            size_hint_y=None,
            height=dp(40),
            font_style="Body2",
            halign="center",
        )
        container.add_widget(self.message_label)

        # Action Buttons
        button_container = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(12),
        )

        cancel_btn = MDFlatButton(
            text=_("screens.import_data.cancel"),
            on_press=self._on_cancel,
        )
        button_container.add_widget(cancel_btn)

        self.import_btn = MDRaisedButton(
            text=_("screens.import_data.import_button"),
            on_press=self._on_import,
            disabled=True,
            md_bg_color=(0.3, 0.6, 0.9, 1),  # Blue
        )
        button_container.add_widget(self.import_btn)

        container.add_widget(button_container)

        layout.add_widget(container)
        self.add_widget(layout)

    def _load_data_counts(self):
        """Load and display current data counts."""
        self.data_counts = get_data_counts()
        count_text = _("screens.import_data.current_data", **self.data_counts)
        self.data_counts_label.text = count_text
        Logger.info(f"ImportDataScreen: Loaded data counts: {self.data_counts}")

    def _on_choose_file(self, *args):
        """Open file picker to select backup file."""
        Logger.info("ImportDataScreen: Opening file picker")

        try:
            from plyer import filechooser

            # Store callback to prevent garbage collection
            self._file_picker_callback = self._on_file_selected

            # Note: On Android, file picker filters are often ignored or cause issues
            # We validate the file extension after selection instead
            # Some Android file pickers also don't start in Downloads by default
            filechooser.open_file(
                on_selection=self._file_picker_callback,
            )
        except Exception as e:
            Logger.error(f"ImportDataScreen: Error opening file picker: {e}")
            self._show_error(_("messages.file_picker_error"))

    def _on_file_selected(self, selection):
        """Handle file selection from file picker."""
        if not selection:
            Logger.info("ImportDataScreen: No file selected")
            return

        self.selected_file = selection[0]
        Logger.info(f"ImportDataScreen: File selected: {self.selected_file}")

        # Validate file extension (Android file pickers often ignore filters)
        from pathlib import Path
        if not self.selected_file.lower().endswith('.zip'):
            Logger.warning(f"ImportDataScreen: Invalid file type selected: {self.selected_file}")
            self._show_error(_("messages.invalid_backup", error="File must be a .zip file"))
            self.selected_file = None
            self._update_file_display()
            self._update_button_state()
            return

        self._update_file_display()
        self._update_button_state()

    def _update_file_display(self):
        """Update the file display label."""
        if self.selected_file:
            from pathlib import Path
            filename = Path(self.selected_file).name
            self.file_display_label.text = _("screens.import_data.file_selected", filename=filename)
        else:
            self.file_display_label.text = _("screens.import_data.no_file")

    def _update_button_state(self):
        """Update import button enabled/disabled state."""
        self.import_btn.disabled = (self.selected_file is None) or self.is_importing

    def _on_import(self, *args):
        """Execute import operation."""
        if not self.selected_file:
            return

        Logger.info(f"ImportDataScreen: Starting import from {self.selected_file}")

        # Show progress
        self.is_importing = True
        self.spinner.active = True
        self.import_btn.text = _("screens.import_data.importing")
        self._update_button_state()

        # Execute import (schedule to allow UI to update)
        Clock.schedule_once(lambda dt: self._do_import(), 0.1)

    def _do_import(self):
        """Perform the actual import operation."""
        try:
            success, error = import_from_csv(self.selected_file)

            self.spinner.active = False
            self.is_importing = False
            self.import_btn.text = _("screens.import_data.import_button")

            if success:
                Logger.info("ImportDataScreen: Import successful")
                # Reload language from database (in case it changed)
                from logic.localization import load_language_from_database
                load_language_from_database()

                self._show_success(_("messages.import_success"))
            else:
                Logger.error(f"ImportDataScreen: Import failed: {error}")
                self._show_error(_("messages.import_error", error=error))
                self._update_button_state()
        except Exception as e:
            Logger.error(f"ImportDataScreen: Unexpected error during import: {e}")
            self.spinner.active = False
            self.is_importing = False
            self.import_btn.text = _("screens.import_data.import_button")
            self._show_error(_("messages.import_error", error=str(e)))
            self._update_button_state()

    def _on_cancel(self, *args):
        """Cancel and navigate back to account tab."""
        Logger.info("ImportDataScreen: Cancelled")
        self._navigate_to_account()

    def _navigate_to_account(self):
        """Navigate back to account tab in main container with full UI refresh."""
        if self.manager:
            # 1. Switch to main container screen
            self.manager.current = "main_container"

            # 2. Get main container instance
            main_container = self.manager.get_screen("main_container")
            if not main_container:
                return

            # 3. Switch to account tab
            if hasattr(main_container, "bottom_nav"):
                main_container.bottom_nav.switch_tab("account")

            # 4. Refresh account content to show updated data counts
            if hasattr(main_container, "account_content"):
                main_container.account_content.refresh_ui()

            # 5. CRITICAL: Invalidate analytics cache (data changed)
            from logic.heatmap_data import HeatmapDataCache
            HeatmapDataCache.clear()  # Clear all cached heatmap data

            # 6. CRITICAL: Reload habits list (habits may have changed)
            if hasattr(main_container, "habits_screen"):
                main_container.habits_screen.load_habits()

    def _show_error(self, message: str):
        """Display error message."""
        self.message_label.text = message
        self.message_label.text_color = (0.8, 0.2, 0.2, 1)  # Red

    def _show_success(self, message: str):
        """Display success message and navigate back after delay."""
        self.message_label.text = message
        self.message_label.text_color = (0, 0.6, 0, 1)  # Green

        # Navigate back after 1.5 seconds
        Clock.schedule_once(lambda dt: self._navigate_to_account(), 1.5)
