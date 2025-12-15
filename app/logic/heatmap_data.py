"""
Heatmap Data Management for HabitForge

Handles data transformation from database completions to heatmap display format.
Includes caching layer to optimize performance and reduce redundant queries.
"""

from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional
from models.database import get_completions_for_habit
from models.schemas import Completion
from kivy.logger import Logger


class HeatmapDataCache:
    """
    Cache for heatmap data to avoid redundant database queries.

    Cache key format: (habit_id, view_type, reference_date_iso)
    Cache value: Dict[date, int] - map of date to completion count
    """

    _cache: Dict[Tuple[int, str, str], Dict[date, int]] = {}

    @staticmethod
    def _get_key(habit_id: int, view_type: str, reference_date: date) -> Tuple[int, str, str]:
        """Generate cache key from parameters."""
        return (habit_id, view_type, reference_date.isoformat())

    @classmethod
    def get(
        cls,
        habit_id: int,
        view_type: str,
        reference_date: date
    ) -> Optional[Dict[date, int]]:
        """
        Retrieve cached data if available.

        Args:
            habit_id: ID of the habit
            view_type: "week", "month", or "year"
            reference_date: Reference date for the period

        Returns:
            Cached completion data or None if not cached
        """
        key = cls._get_key(habit_id, view_type, reference_date)
        data = cls._cache.get(key)

        if data is not None:
            Logger.debug(
                f"HeatmapDataCache: Cache HIT for habit {habit_id}, {view_type}, {reference_date}"
            )
        else:
            Logger.debug(
                f"HeatmapDataCache: Cache MISS for habit {habit_id}, {view_type}, {reference_date}"
            )

        return data

    @classmethod
    def set(
        cls,
        habit_id: int,
        view_type: str,
        reference_date: date,
        data: Dict[date, int]
    ):
        """
        Store data in cache.

        Args:
            habit_id: ID of the habit
            view_type: "week", "month", or "year"
            reference_date: Reference date for the period
            data: Completion data to cache
        """
        key = cls._get_key(habit_id, view_type, reference_date)
        cls._cache[key] = data

        Logger.debug(
            f"HeatmapDataCache: Cached data for habit {habit_id}, {view_type}, {reference_date}"
        )

    @classmethod
    def invalidate_habit(cls, habit_id: int):
        """
        Clear all cached data for a specific habit.

        Called when a completion is logged to ensure fresh data.

        Args:
            habit_id: ID of the habit to invalidate
        """
        keys_to_remove = [key for key in cls._cache if key[0] == habit_id]

        for key in keys_to_remove:
            del cls._cache[key]

        if keys_to_remove:
            Logger.debug(
                f"HeatmapDataCache: Invalidated {len(keys_to_remove)} cache entries for habit {habit_id}"
            )

    @classmethod
    def clear(cls):
        """Clear entire cache."""
        cls._cache.clear()
        Logger.debug("HeatmapDataCache: Cleared entire cache")


def transform_completions_to_heatmap(
    completions: List[Completion],
    start_date: date,
    end_date: date
) -> Dict[date, int]:
    """
    Transform completion list to date->count map for heatmap display.

    Fills gaps with 0 for dates with no completions.

    Args:
        completions: List of Completion objects from database
        start_date: First date in range
        end_date: Last date in range (inclusive)

    Returns:
        Dict mapping each date in range to its completion count
    """
    # Create map from completions
    completion_map = {}
    for completion in completions:
        # Parse date if it's a string (from SQLite)
        completion_date = completion.date
        if isinstance(completion_date, str):
            completion_date = date.fromisoformat(completion_date)

        completion_map[completion_date] = completion.count

    # Fill all dates in range (including gaps with 0)
    heatmap_data = {}
    current = start_date

    while current <= end_date:
        heatmap_data[current] = completion_map.get(current, 0)
        current += timedelta(days=1)

    Logger.debug(
        f"HeatmapData: Transformed {len(completions)} completions into {len(heatmap_data)} date entries"
    )

    return heatmap_data


def get_heatmap_data(
    habit_id: int,
    start_date: date,
    end_date: date,
    view_type: str,
    reference_date: date,
    use_cache: bool = True
) -> Dict[date, int]:
    """
    Get heatmap data for a habit and date range.

    Checks cache first, then queries database if needed.

    Args:
        habit_id: ID of the habit
        start_date: First date in range
        end_date: Last date in range (inclusive)
        view_type: "week", "month", or "year" (for cache key)
        reference_date: Reference date (for cache key)
        use_cache: Whether to use/update cache (default True)

    Returns:
        Dict mapping each date in range to its completion count
    """
    # Check cache first (if enabled)
    if use_cache:
        cached_data = HeatmapDataCache.get(habit_id, view_type, reference_date)
        if cached_data is not None:
            return cached_data

    # Cache miss or disabled - query database
    Logger.debug(
        f"HeatmapData: Fetching completions for habit {habit_id} from {start_date} to {end_date}"
    )

    completions = get_completions_for_habit(habit_id, start_date, end_date)

    # Transform to heatmap format
    heatmap_data = transform_completions_to_heatmap(completions, start_date, end_date)

    # Store in cache (if enabled)
    if use_cache:
        HeatmapDataCache.set(habit_id, view_type, reference_date, heatmap_data)

    return heatmap_data


def calculate_overall_percentage(
    completion_data: Dict[date, int],
    goal_count: int,
    start_date: date,
    end_date: date
) -> float:
    """
    Calculate overall completion percentage for a period.

    Args:
        completion_data: Map of date to completion count
        goal_count: Goal count per day
        start_date: First date in period
        end_date: Last date in period

    Returns:
        Overall completion percentage (0-100)
    """
    total_completions = sum(completion_data.values())
    total_days = (end_date - start_date).days + 1
    max_possible = total_days * goal_count

    if max_possible == 0:
        return 0.0

    percentage = min(100.0, (total_completions / max_possible) * 100)

    return round(percentage, 1)
