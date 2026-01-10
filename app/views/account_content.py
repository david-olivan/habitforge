"""
Account Content for HabitForge

Account settings screen with localization and data management features.
"""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.snackbar import MDSnackbar
from kivy.metrics import dp
from kivy.logger import Logger

from logic.localization import _, set_language, get_current_language
from logic.data_manager import export_to_csv
from config.constants import (
    EXPORT_BUTTON_COLOR,
    IMPORT_BUTTON_COLOR,
    DELETE_BUTTON_COLOR,
)


class AccountContent(MDBoxLayout):
    """
    Account settings screen with two main sections:
    1. Language selection (English/Spanish)
    2. Data management (Export/Import/Delete)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(20)
        self.spacing = dp(16)

        # Build UI
        self._build_ui()

        Logger.info("AccountContent: Initialized")

    def _build_ui(self):
        """Build the complete account settings UI."""
        # Title
        title = MDLabel(
            text=_("account.title"),
            font_style="H5",
            size_hint_y=None,
            height=dp(40),
        )
        self.add_widget(title)

        # Spacer
        self.add_widget(MDLabel(size_hint_y=None, height=dp(12)))

        # Localization section
        self.add_widget(self._build_localization_section())

        # Spacer
        self.add_widget(MDLabel(size_hint_y=None, height=dp(24)))

        # Data management section
        self.add_widget(self._build_data_management_section())

        # Bottom spacer (push content to top)
        self.add_widget(MDLabel())

    def _build_localization_section(self) -> MDCard:
        """
        Build the localization section with language selector.

        Returns:
            MDCard: Card containing language selection UI
        """
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(140),
        )

        # Section title
        section_title = MDLabel(
            text=_("account.localization_section"),
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(24),
        )
        card.add_widget(section_title)

        # Language buttons container
        lang_container = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(80),
        )

        # Get current language
        current_lang = get_current_language()

        # English button
        en_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_x=0.5,
        )

        self.en_button = MDIconButton(
            icon="alpha-e-circle",
            icon_size="48sp",
            on_release=lambda x: self._on_language_selected("en"),
        )
        # Highlight current language
        if current_lang == "en":
            self.en_button.md_bg_color = (0.3, 0.3, 0.3, 1)

        en_label = MDLabel(
            text=_("account.english"),
            halign="center",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20),
        )

        en_box.add_widget(self.en_button)
        en_box.add_widget(en_label)
        lang_container.add_widget(en_box)

        # Spanish button
        es_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_x=0.5,
        )

        self.es_button = MDIconButton(
            icon="alpha-s-circle",
            icon_size="48sp",
            on_release=lambda x: self._on_language_selected("es"),
        )
        # Highlight current language
        if current_lang == "es":
            self.es_button.md_bg_color = (0.3, 0.3, 0.3, 1)

        es_label = MDLabel(
            text=_("account.spanish"),
            halign="center",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20),
        )

        es_box.add_widget(self.es_button)
        es_box.add_widget(es_label)
        lang_container.add_widget(es_box)

        card.add_widget(lang_container)
        return card

    def _build_data_management_section(self) -> MDCard:
        """
        Build the data management section with export/import/delete buttons.

        Returns:
            MDCard: Card containing data management buttons
        """
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(240),
        )

        # Section title
        section_title = MDLabel(
            text=_("account.data_section"),
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(24),
        )
        card.add_widget(section_title)

        # Export button
        export_btn = MDRaisedButton(
            text=_("account.export_button"),
            md_bg_color=EXPORT_BUTTON_COLOR,
            size_hint_x=1,
            size_hint_y=None,
            height=dp(48),
            on_release=self._on_export_pressed,
        )
        card.add_widget(export_btn)

        # Import button
        import_btn = MDRaisedButton(
            text=_("account.import_button"),
            md_bg_color=IMPORT_BUTTON_COLOR,
            size_hint_x=1,
            size_hint_y=None,
            height=dp(48),
            on_release=self._on_import_pressed,
        )
        card.add_widget(import_btn)

        # Delete button
        delete_btn = MDRaisedButton(
            text=_("account.delete_button"),
            md_bg_color=DELETE_BUTTON_COLOR,
            size_hint_x=1,
            size_hint_y=None,
            height=dp(48),
            on_release=self._on_delete_pressed,
        )
        card.add_widget(delete_btn)

        return card

    def _on_language_selected(self, lang_code: str):
        """
        Handle language selection.

        Args:
            lang_code: Language code ('en' or 'es')
        """
        Logger.info(f"AccountContent: Language selected: {lang_code}")

        # Change language
        success = set_language(lang_code)
        if success:
            # Update UI with new language
            self.refresh_ui()

            # Show success message
            self._show_snackbar(_("messages.language_changed"))

            # Update button highlights
            current_lang = get_current_language()
            self.en_button.md_bg_color = (0.3, 0.3, 0.3, 1) if current_lang == "en" else (0, 0, 0, 0)
            self.es_button.md_bg_color = (0.3, 0.3, 0.3, 1) if current_lang == "es" else (0, 0, 0, 0)
        else:
            self._show_snackbar(_("messages.error"), is_error=True)

    def _on_export_pressed(self, *args):
        """Handle export button press."""
        Logger.info("AccountContent: Export button pressed")

        success, result = export_to_csv()
        if success:
            # result is filename
            message = _("messages.export_success", filename=result)
            self._show_snackbar(message)
        else:
            # result is error message
            message = _("messages.export_error", error=result)
            self._show_snackbar(message, is_error=True)

    def _on_import_pressed(self, *args):
        """Navigate to import data screen."""
        Logger.info("AccountContent: Import button pressed - navigating to import screen")
        self._navigate_to_screen("import_data")

    def _on_delete_pressed(self, *args):
        """Navigate to delete data screen."""
        Logger.info("AccountContent: Delete button pressed - navigating to delete screen")
        self._navigate_to_screen("delete_data")

    def _navigate_to_screen(self, screen_name: str):
        """
        Navigate to a specific screen.

        Args:
            screen_name: Name of the screen to navigate to
        """
        # Navigate up through widget hierarchy to find the MainContainerScreen
        # MainContainerScreen is an MDScreen, so it has .manager pointing to the root MDScreenManager
        widget = self.parent
        while widget:
            # Look for MainContainerScreen (it's an MDScreen with name="main_container")
            if hasattr(widget, 'name') and widget.name == "main_container":
                if hasattr(widget, 'manager') and widget.manager:
                    Logger.info(f"AccountContent: Found MainContainerScreen, navigating to {screen_name}")
                    widget.manager.current = screen_name
                    return
            widget = widget.parent

        Logger.error(f"AccountContent: Could not find screen manager to navigate to {screen_name}")

    def _show_snackbar(self, message: str, is_error: bool = False):
        """
        Show a snackbar notification.

        Args:
            message: Message to display
            is_error: Whether this is an error message (changes color)
        """
        from kivymd.uix.label import MDLabel

        snackbar = MDSnackbar(
            MDLabel(
                text=message,
            ),
            duration=3,
            bg_color=(0.8, 0.2, 0.2, 1) if is_error else (0.2, 0.6, 0.2, 1),
        )
        snackbar.open()
        Logger.debug(f"AccountContent: Snackbar shown: {message}")

    def refresh_ui(self):
        """
        Refresh the UI with updated translations.

        Rebuilds the entire UI to apply new language strings.
        """
        Logger.info("AccountContent: Refreshing UI with new language")
        self.clear_widgets()
        self._build_ui()
