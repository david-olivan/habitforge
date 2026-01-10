"""
Delete Data Screen for HabitForge

Full-screen view for deleting all data with text confirmation.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.clock import Clock

from logic.data_manager import get_data_counts, delete_all_data
from logic.localization import _
from config.constants import DELETE_BUTTON_COLOR, BRAND_PRIMARY_RGB


class DeleteDataScreen(MDScreen):
    """
    Screen for deleting all data.

    Shows warnings about permanent deletion, requires text confirmation,
    and executes delete operation.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "delete_data"

        # State
        self.confirmation_text = ""
        self.data_counts = {"habit_count": 0, "completion_count": 0}
        self.is_deleting = False

        # Build UI
        self._build_ui()

        Logger.info(f"DeleteDataScreen: Initialized with name='{self.name}'")

    def on_pre_enter(self):
        """Reset state before screen appears."""
        Logger.info("DeleteDataScreen: Entering screen")
        self.confirmation_text = ""
        self.is_deleting = False
        self.confirmation_field.text = ""
        self._load_data_counts()
        self._update_button_state()

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
            title=_("screens.delete_data.title"),
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

        # Danger Warning Card
        warning_card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(180),
            md_bg_color=(1, 0.9, 0.9, 1),  # Light red danger color
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
            text_color=DELETE_BUTTON_COLOR,  # Red warning color
            disabled=True,  # Not clickable, just for display
            size_hint=(None, None),
            size=(dp(32), dp(32)),
        )
        warning_title_container.add_widget(warning_icon)

        warning_title = MDLabel(
            text=_("screens.delete_data.warning_title"),
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=DELETE_BUTTON_COLOR,
            valign="middle",
        )
        warning_title_container.add_widget(warning_title)
        warning_card.add_widget(warning_title_container)

        # Warning message
        warning_message = MDLabel(
            text=_("screens.delete_data.warning_message"),
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
            text=_("screens.delete_data.subtitle"),
            font_style="Caption",
            size_hint_y=None,
            height=dp(24),
        )
        warning_card.add_widget(subtitle)

        container.add_widget(warning_card)

        # Confirmation Label
        confirmation_label = MDLabel(
            text=_("screens.delete_data.confirmation_label"),
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(32),
        )
        container.add_widget(confirmation_label)

        # Confirmation Text Field
        self.confirmation_field = MDTextField(
            hint_text=_("screens.delete_data.confirmation_placeholder"),
            size_hint_y=None,
            height=dp(56),
            mode="rectangle",
        )
        self.confirmation_field.bind(text=self._on_confirmation_text_change)
        container.add_widget(self.confirmation_field)

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
            text=_("screens.delete_data.cancel"),
            on_press=self._on_cancel,
        )
        button_container.add_widget(cancel_btn)

        self.delete_btn = MDRaisedButton(
            text=_("screens.delete_data.delete_button"),
            on_press=self._on_delete,
            disabled=True,
            md_bg_color=DELETE_BUTTON_COLOR,
        )
        button_container.add_widget(self.delete_btn)

        container.add_widget(button_container)

        layout.add_widget(container)
        self.add_widget(layout)

    def _load_data_counts(self):
        """Load and display current data counts."""
        self.data_counts = get_data_counts()
        count_text = _("screens.delete_data.current_data", **self.data_counts)
        self.data_counts_label.text = count_text
        Logger.info(f"DeleteDataScreen: Loaded data counts: {self.data_counts}")

    def _on_confirmation_text_change(self, instance, value):
        """Handle confirmation text field changes."""
        self.confirmation_text = value
        self._update_button_state()

        # Visual feedback when typed correctly
        if value.upper() == "DELETE":
            self.confirmation_field.text_color = (0, 0.6, 0, 1)  # Green
        else:
            self.confirmation_field.text_color = (0, 0, 0, 1)  # Black

    def _update_button_state(self):
        """Update delete button enabled/disabled state."""
        # Enable only if "DELETE" is typed (case-insensitive)
        is_confirmed = self.confirmation_text.upper() == "DELETE"
        self.delete_btn.disabled = (not is_confirmed) or self.is_deleting

    def _on_delete(self, *args):
        """Execute delete operation."""
        if self.confirmation_text.upper() != "DELETE":
            return

        Logger.info("DeleteDataScreen: Starting delete all data operation")

        # Show progress
        self.is_deleting = True
        self.spinner.active = True
        self.delete_btn.text = _("screens.delete_data.deleting")
        self._update_button_state()

        # Execute delete (schedule to allow UI to update)
        Clock.schedule_once(lambda dt: self._do_delete(), 0.1)

    def _do_delete(self):
        """Perform the actual delete operation."""
        try:
            success, error = delete_all_data()

            self.spinner.active = False
            self.is_deleting = False
            self.delete_btn.text = _("screens.delete_data.delete_button")

            if success:
                Logger.info("DeleteDataScreen: Delete successful")
                # Reload language from database (reset to English)
                from logic.localization import load_language_from_database
                load_language_from_database()

                self._show_success(_("messages.delete_success"))
            else:
                Logger.error(f"DeleteDataScreen: Delete failed: {error}")
                self._show_error(_("messages.delete_error", error=error))
                self._update_button_state()
        except Exception as e:
            Logger.error(f"DeleteDataScreen: Unexpected error during delete: {e}")
            self.spinner.active = False
            self.is_deleting = False
            self.delete_btn.text = _("screens.delete_data.delete_button")
            self._show_error(_("messages.delete_error", error=str(e)))
            self._update_button_state()

    def _on_cancel(self, *args):
        """Cancel and navigate back to account tab."""
        Logger.info("DeleteDataScreen: Cancelled")
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
