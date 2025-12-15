"""
Heatmap Grid Component for HabitForge

Grid layout containing heatmap cells for calendar visualization.
Dynamically calculates grid dimensions based on view type (week/month/year).
"""

from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from datetime import date, timedelta
from typing import Dict, Tuple, Optional
from dateutil.relativedelta import relativedelta

from components.heatmap_cell import HeatmapCell
from logic.date_utils import get_period_boundaries, get_today


class HeatmapGrid(GridLayout):
    """
    Grid layout displaying heatmap cells for a date range.

    Supports three view types:
    - Week: 7 columns x 1 row (Mon-Sun)
    - Month: 7 columns x 4-6 rows (calendar grid)
    - Year: 53 columns x 7 rows (weeks x days, GitHub style)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Grid configuration
        self.cols = 7  # Default to week view
        self.spacing = dp(2)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

    def populate_grid(
        self,
        start_date: date,
        end_date: date,
        completion_data: Dict[date, int],
        habit_color: str,
        goal_count: int,
        goal_type: str
    ):
        """
        Clear and rebuild grid with cells for the specified date range.

        Args:
            start_date: First date to display
            end_date: Last date to display (inclusive)
            completion_data: Map of {date: completion_count}
            habit_color: Hex color for this habit (e.g., "#E57373")
            goal_count: Goal count to calculate percentage
            goal_type: 'daily', 'weekly', or 'monthly'
        """
        # Clear existing cells
        self.clear_widgets()

        # Get today's date for highlighting
        today = get_today()

        # Calculate grid height based on cell count and spacing
        total_days = (end_date - start_date).days + 1
        rows = (total_days + self.cols - 1) // self.cols  # Ceiling division
        cell_size = dp(20)

        # Get spacing value (it's a list [x, y], we want y for vertical spacing)
        spacing_value = self.spacing[1] if isinstance(self.spacing, (list, tuple)) else self.spacing
        spacing_total = (rows - 1) * spacing_value

        self.height = rows * cell_size + spacing_total

        # Calculate percentage per completion based on goal type
        if goal_type == 'daily':
            # For daily: each completion is a fraction of the daily goal
            # E.g., goal=2, 1 completion = 50%
            percentage_per_completion = (100.0 / goal_count) if goal_count > 0 else 0
        elif goal_type == 'weekly':
            # For weekly: spread goal across 7 days
            # E.g., goal=3/week, each completion = 33.33%
            percentage_per_completion = (100.0 / goal_count) if goal_count > 0 else 0
        elif goal_type == 'monthly':
            # For monthly: spread goal across days in month
            # E.g., goal=10/month, each completion = 10%
            percentage_per_completion = (100.0 / goal_count) if goal_count > 0 else 0
        else:
            percentage_per_completion = (100.0 / goal_count) if goal_count > 0 else 0

        # Create cells for each date in range
        current_date = start_date
        while current_date <= end_date:
            # Get completion count for this day
            count = completion_data.get(current_date, 0)

            # Calculate percentage: count * percentage_per_completion
            # Cap at 100% regardless of over-completion
            percentage = min(100, count * percentage_per_completion)

            # Create cell
            cell = HeatmapCell(
                cell_date=current_date,
                completion_percentage=percentage,
                habit_color=habit_color,
                is_today=(current_date == today)
            )

            self.add_widget(cell)
            current_date += timedelta(days=1)

    @staticmethod
    def calculate_grid_dimensions(
        view_type: str,
        reference_date: Optional[date] = None
    ) -> Tuple[int, int, date, date]:
        """
        Calculate grid dimensions and date range for a view type.

        Args:
            view_type: "week", "month", or "year"
            reference_date: Date to calculate period for (defaults to today)

        Returns:
            Tuple of (cols, rows, start_date, end_date)

        Raises:
            ValueError: If view_type is invalid
        """
        if reference_date is None:
            reference_date = get_today()

        if view_type == "week":
            # 7 columns (Mon-Sun), 1 row
            start, end = get_period_boundaries("weekly", reference_date)
            return (7, 1, start, end)

        elif view_type == "month":
            # 7 columns, 4-6 rows (calendar grid)
            start, end = get_period_boundaries("monthly", reference_date)

            # Pad to start on Monday, end on Sunday (full calendar weeks)
            days_to_monday = start.weekday()  # 0=Monday, 6=Sunday
            start_padded = start - timedelta(days=days_to_monday)

            days_to_sunday = 6 - end.weekday()
            end_padded = end + timedelta(days=days_to_sunday)

            total_days = (end_padded - start_padded).days + 1
            rows = total_days // 7

            return (7, rows, start_padded, end_padded)

        elif view_type == "year":
            # Year view: Show full year as 53 weeks x 7 days (GitHub style)
            # Alternative: 12 months in a simpler grid
            # For now, using simplified approach: all days of year in 7-column grid
            year_start = reference_date.replace(month=1, day=1)
            year_end = reference_date.replace(month=12, day=31)

            # Pad to start on Monday
            days_to_monday = year_start.weekday()
            start_padded = year_start - timedelta(days=days_to_monday)

            # Pad to end on Sunday
            days_to_sunday = 6 - year_end.weekday()
            end_padded = year_end + timedelta(days=days_to_sunday)

            total_days = (end_padded - start_padded).days + 1
            rows = total_days // 7

            return (7, rows, start_padded, end_padded)

        else:
            raise ValueError(
                f"Invalid view_type '{view_type}'. Must be 'week', 'month', or 'year'."
            )

    def set_view_type(self, view_type: str, reference_date: Optional[date] = None):
        """
        Configure grid for a specific view type and recalculate dimensions.

        Args:
            view_type: "week", "month", or "year"
            reference_date: Date to calculate period for (defaults to today)
        """
        cols, rows, start, end = self.calculate_grid_dimensions(view_type, reference_date)
        self.cols = cols

        # Note: Grid will be populated separately via populate_grid()
        # This method just sets the column count
