"""
Data Manager for HabitForge

Handles export, import, and deletion of all app data.
Creates CSV backups and restores data from backup files.
"""

import csv
import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Optional
from kivy.logger import Logger


def get_downloads_path() -> Path:
    """
    Get the path to the Downloads folder.

    Returns:
        Path: Path to Downloads folder (Android or desktop)
    """
    try:
        # Try to get Android Downloads folder
        from android.storage import primary_external_storage_path
        downloads = Path(primary_external_storage_path()) / "Download"
        if downloads.exists():
            Logger.info(f"DataManager: Using Android Downloads path: {downloads}")
            return downloads
    except Exception as e:
        Logger.debug(f"DataManager: Not on Android or storage unavailable: {e}")

    # Fallback to user's Downloads folder (Windows/Linux/Mac)
    downloads = Path.home() / "Downloads"
    if downloads.exists():
        Logger.info(f"DataManager: Using Desktop Downloads path: {downloads}")
        return downloads

    # Last resort: use current directory
    Logger.warning("DataManager: Downloads folder not found, using current directory")
    return Path.cwd()


def get_data_counts() -> Dict[str, int]:
    """
    Get counts of habits and completions for confirmation dialogs.

    Returns:
        Dict[str, int]: Dictionary with 'habit_count' and 'completion_count'
    """
    try:
        from models.database import get_connection

        with get_connection() as conn:
            cursor = conn.cursor()

            # Count habits (excluding archived)
            cursor.execute("SELECT COUNT(*) FROM habits WHERE archived = 0")
            habit_count = cursor.fetchone()[0]

            # Count completions
            cursor.execute("SELECT COUNT(*) FROM completions")
            completion_count = cursor.fetchone()[0]

            Logger.info(
                f"DataManager: Data counts - {habit_count} habits, {completion_count} completions"
            )
            return {"habit_count": habit_count, "completion_count": completion_count}
    except Exception as e:
        Logger.error(f"DataManager: Error getting data counts: {e}")
        return {"habit_count": 0, "completion_count": 0}


def validate_backup_zip(zip_path: str) -> Tuple[bool, str]:
    """
    Validate that a backup ZIP file has the correct structure.

    Args:
        zip_path: Path to ZIP file

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        if not os.path.exists(zip_path):
            return False, "File not found"

        with zipfile.ZipFile(zip_path, 'r') as zipf:
            files = zipf.namelist()

            # Check required files exist
            required = ['habits.csv', 'completions.csv', 'settings.csv']
            missing = [f for f in required if f not in files]

            if missing:
                return False, f"Missing required files: {', '.join(missing)}"

            return True, ""

    except zipfile.BadZipFile:
        return False, "Not a valid ZIP file"
    except Exception as e:
        return False, str(e)


def export_to_csv() -> Tuple[bool, str]:
    """
    Export all data (habits, completions, settings) to a ZIP file containing CSVs.

    Creates a ZIP file in the Downloads folder with timestamp in filename.
    Filename format: habitforge_backup_YYYYMMDD_HHMMSS.zip

    Returns:
        Tuple[bool, str]: (success, filename_or_error_message)
    """
    try:
        from models.database import get_connection

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"habitforge_backup_{timestamp}.zip"
        downloads_path = get_downloads_path()
        zip_path = downloads_path / zip_filename

        Logger.info(f"DataManager: Starting export to {zip_path}")

        # Create temporary directory for CSV files
        temp_dir = downloads_path / f"temp_{timestamp}"
        temp_dir.mkdir(exist_ok=True)

        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # Export habits table
                habits_csv = temp_dir / "habits.csv"
                cursor.execute("SELECT * FROM habits")
                rows = cursor.fetchall()
                if rows:
                    with open(habits_csv, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        # Write header
                        writer.writerow([desc[0] for desc in cursor.description])
                        # Write data
                        writer.writerows(rows)
                    Logger.info(f"DataManager: Exported {len(rows)} habits")

                # Export completions table
                completions_csv = temp_dir / "completions.csv"
                cursor.execute("SELECT * FROM completions")
                rows = cursor.fetchall()
                if rows:
                    with open(completions_csv, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([desc[0] for desc in cursor.description])
                        writer.writerows(rows)
                    Logger.info(f"DataManager: Exported {len(rows)} completions")

                # Export settings table
                settings_csv = temp_dir / "settings.csv"
                cursor.execute("SELECT * FROM settings")
                rows = cursor.fetchall()
                if rows:
                    with open(settings_csv, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([desc[0] for desc in cursor.description])
                        writer.writerows(rows)
                    Logger.info(f"DataManager: Exported {len(rows)} settings")

            # Create ZIP file
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for csv_file in temp_dir.glob("*.csv"):
                    zipf.write(csv_file, csv_file.name)
                    Logger.debug(f"DataManager: Added {csv_file.name} to ZIP")

            Logger.info(f"DataManager: Export successful to {zip_filename}")
            return True, zip_filename

        finally:
            # Clean up temporary CSV files
            for csv_file in temp_dir.glob("*.csv"):
                csv_file.unlink()
            temp_dir.rmdir()
            Logger.debug("DataManager: Cleaned up temporary files")

    except Exception as e:
        error_msg = str(e)
        Logger.error(f"DataManager: Export failed: {error_msg}")
        return False, error_msg


def import_from_csv(zip_path: str) -> Tuple[bool, str]:
    """
    Import data from a ZIP backup file.

    Wipes existing data and replaces with data from CSV files.
    Language setting is reset to English default.

    Args:
        zip_path: Path to the ZIP backup file

    Returns:
        Tuple[bool, str]: (success, error_message_if_failed)
    """
    try:
        from models.database import get_connection

        # CRITICAL: Validate ZIP structure BEFORE wiping data
        is_valid, error = validate_backup_zip(zip_path)
        if not is_valid:
            Logger.error(f"DataManager: Invalid backup file: {error}")
            return False, f"Invalid backup: {error}"

        Logger.info(f"DataManager: Starting import from {zip_path}")

        # Extract ZIP to temporary directory
        temp_dir = Path(zip_path).parent / f"temp_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        temp_dir.mkdir(exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, "r") as zipf:
                zipf.extractall(temp_dir)
                Logger.debug(f"DataManager: Extracted ZIP to {temp_dir}")

            with get_connection() as conn:
                cursor = conn.cursor()

                # Wipe existing data (CASCADE will delete completions)
                Logger.info("DataManager: Wiping existing data...")
                cursor.execute("DELETE FROM habits")
                cursor.execute("DELETE FROM completions")
                cursor.execute("DELETE FROM settings")
                cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('habits', 'completions')")
                conn.commit()

                # Import habits
                habits_csv = temp_dir / "habits.csv"
                if habits_csv.exists():
                    with open(habits_csv, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)
                        for row in rows:
                            cursor.execute(
                                """
                                INSERT INTO habits (id, name, color, goal_type, goal_count, created_at, archived)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    row["id"],
                                    row["name"],
                                    row["color"],
                                    row["goal_type"],
                                    row["goal_count"],
                                    row["created_at"],
                                    row["archived"],
                                ),
                            )
                        Logger.info(f"DataManager: Imported {len(rows)} habits")

                # Import completions
                completions_csv = temp_dir / "completions.csv"
                if completions_csv.exists():
                    with open(completions_csv, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)
                        for row in rows:
                            cursor.execute(
                                """
                                INSERT INTO completions (id, habit_id, date, count, completed_at)
                                VALUES (?, ?, ?, ?, ?)
                                """,
                                (
                                    row["id"],
                                    row["habit_id"],
                                    row["date"],
                                    row["count"],
                                    row["completed_at"],
                                ),
                            )
                        Logger.info(f"DataManager: Imported {len(rows)} completions")

                # Import settings
                settings_csv = temp_dir / "settings.csv"
                if settings_csv.exists():
                    with open(settings_csv, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)
                        for row in rows:
                            cursor.execute(
                                """
                                INSERT INTO settings (key, value, updated_at)
                                VALUES (?, ?, ?)
                                """,
                                (row["key"], row["value"], row.get("updated_at", "CURRENT_TIMESTAMP")),
                            )
                        Logger.info(f"DataManager: Imported {len(rows)} settings")

                conn.commit()
                Logger.info("DataManager: Import successful")
                return True, ""

        finally:
            # Clean up temporary files
            for file in temp_dir.glob("*"):
                file.unlink()
            temp_dir.rmdir()
            Logger.debug("DataManager: Cleaned up temporary import files")

    except Exception as e:
        error_msg = str(e)
        Logger.error(f"DataManager: Import failed: {error_msg}")
        return False, error_msg


def delete_all_data() -> Tuple[bool, str]:
    """
    Delete all data from the database.

    Wipes habits, completions, and settings tables.
    Resets language to English default.

    Returns:
        Tuple[bool, str]: (success, error_message_if_failed)
    """
    try:
        from models.database import get_connection

        Logger.info("DataManager: Starting delete all data operation")

        with get_connection() as conn:
            cursor = conn.cursor()

            # Delete all data
            cursor.execute("DELETE FROM habits")  # CASCADE deletes completions
            cursor.execute("DELETE FROM completions")
            cursor.execute("DELETE FROM settings")

            # Reset autoincrement counters
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('habits', 'completions')")

            # Reset language to English default
            cursor.execute(
                """
                INSERT INTO settings (key, value, updated_at)
                VALUES ('language', 'en', CURRENT_TIMESTAMP)
                """
            )

            conn.commit()
            Logger.info("DataManager: All data deleted successfully")
            return True, ""

    except Exception as e:
        error_msg = str(e)
        Logger.error(f"DataManager: Delete all data failed: {error_msg}")
        return False, error_msg
