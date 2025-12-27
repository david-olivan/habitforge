"""
Localization Manager for HabitForge

Handles loading and managing translations for multiple languages.
Uses JSON files for simple translation storage.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from kivy.logger import Logger


class LocalizationManager:
    """
    Singleton class to manage app localization.

    Loads translation strings from JSON files and provides
    access to translated strings with formatting support.
    """

    _instance: Optional["LocalizationManager"] = None
    _translations: Dict[str, any] = {}
    _current_language: str = "en"
    _available_languages: List[str] = ["en", "es"]

    def __new__(cls):
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize localization manager."""
        # Only initialize once (singleton)
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._load_language(self._current_language)

    def _get_strings_path(self) -> Path:
        """
        Get the path to the strings directory.

        Returns:
            Path: Path to app/config/strings directory
        """
        # Get path relative to this file (app/logic/localization.py)
        return Path(__file__).parent.parent / "config" / "strings"

    def _load_language(self, lang_code: str) -> bool:
        """
        Load translation strings from JSON file.

        Args:
            lang_code: Language code (e.g., 'en', 'es')

        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            strings_path = self._get_strings_path()
            json_path = strings_path / f"{lang_code}.json"

            if not json_path.exists():
                Logger.error(
                    f"Localization: Translation file not found: {json_path}"
                )
                return False

            with open(json_path, "r", encoding="utf-8") as f:
                self._translations = json.load(f)

            self._current_language = lang_code
            Logger.info(
                f"Localization: Loaded language '{lang_code}' from {json_path}"
            )
            return True
        except json.JSONDecodeError as e:
            Logger.error(f"Localization: Invalid JSON in {lang_code}.json: {e}")
            return False
        except Exception as e:
            Logger.error(f"Localization: Error loading language '{lang_code}': {e}")
            return False

    def get_string(self, key_path: str, **kwargs) -> str:
        """
        Get a translated string by key path.

        Key paths use dot notation to access nested keys:
        - "app_name" → translations["app_name"]
        - "tabs.habits" → translations["tabs"]["habits"]
        - "dialogs.import_warning" → translations["dialogs"]["import_warning"]

        Supports string formatting with named placeholders:
        - get_string("dialogs.import_warning", habit_count=5, completion_count=120)

        Args:
            key_path: Dot-separated path to translation key
            **kwargs: Named arguments for string formatting

        Returns:
            str: Translated string, or key_path if not found
        """
        try:
            # Navigate through nested dictionaries using dot notation
            keys = key_path.split(".")
            value = self._translations

            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    Logger.warning(
                        f"Localization: Key '{key_path}' not found in '{self._current_language}'"
                    )
                    return key_path  # Return key as fallback

            # Format string with kwargs if provided
            if kwargs and isinstance(value, str):
                return value.format(**kwargs)

            return str(value)
        except Exception as e:
            Logger.error(f"Localization: Error getting string '{key_path}': {e}")
            return key_path

    def set_language(self, lang_code: str) -> bool:
        """
        Switch to a different language.

        Args:
            lang_code: Language code (e.g., 'en', 'es')

        Returns:
            bool: True if language switched successfully, False otherwise
        """
        if lang_code not in self._available_languages:
            Logger.error(
                f"Localization: Unsupported language '{lang_code}'. "
                f"Available: {self._available_languages}"
            )
            return False

        if lang_code == self._current_language:
            Logger.debug(f"Localization: Language '{lang_code}' already active")
            return True

        success = self._load_language(lang_code)
        if success:
            # Persist language preference to database
            from models.database import set_setting

            set_setting("language", lang_code)
            Logger.info(f"Localization: Language changed to '{lang_code}'")
        return success

    def get_current_language(self) -> str:
        """
        Get the currently active language code.

        Returns:
            str: Current language code (e.g., 'en', 'es')
        """
        return self._current_language

    def get_available_languages(self) -> List[str]:
        """
        Get list of available language codes.

        Returns:
            List[str]: List of available language codes
        """
        return self._available_languages.copy()

    def load_from_database(self) -> bool:
        """
        Load language preference from database.

        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            from models.database import get_setting

            lang_code = get_setting("language")
            if lang_code and lang_code in self._available_languages:
                return self._load_language(lang_code)
            else:
                Logger.info(
                    "Localization: No language preference in database, using default 'en'"
                )
                return True
        except Exception as e:
            Logger.error(
                f"Localization: Error loading language from database: {e}"
            )
            return False


# Singleton instance
_localization_manager = LocalizationManager()


def _(key_path: str, **kwargs) -> str:
    """
    Shorthand function to get translated strings.

    This is the recommended way to get translations in the app.

    Examples:
        _("app_name") → "HabitForge"
        _("tabs.habits") → "Habits"
        _("dialogs.import_warning", habit_count=5, completion_count=120)
            → "This will delete 5 habits and 120 completions"

    Args:
        key_path: Dot-separated path to translation key
        **kwargs: Named arguments for string formatting

    Returns:
        str: Translated string
    """
    return _localization_manager.get_string(key_path, **kwargs)


def set_language(lang_code: str) -> bool:
    """
    Switch to a different language.

    Args:
        lang_code: Language code (e.g., 'en', 'es')

    Returns:
        bool: True if language switched successfully
    """
    return _localization_manager.set_language(lang_code)


def get_current_language() -> str:
    """
    Get the currently active language code.

    Returns:
        str: Current language code (e.g., 'en', 'es')
    """
    return _localization_manager.get_current_language()


def get_available_languages() -> List[str]:
    """
    Get list of available language codes.

    Returns:
        List[str]: List of available language codes
    """
    return _localization_manager.get_available_languages()


def load_language_from_database() -> bool:
    """
    Load language preference from database.

    Should be called once at app startup.

    Returns:
        bool: True if loaded successfully
    """
    return _localization_manager.load_from_database()
