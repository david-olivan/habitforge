"""
Unit Tests for Date Utilities

Tests date calculation functions for daily, weekly, and monthly periods.
These are pure Python functions with no external dependencies.
"""

import pytest
import sys
from datetime import date, timedelta
from pathlib import Path

# Add app directory to path for imports
app_dir = Path(__file__).parent.parent.parent.parent / "app"
sys.path.insert(0, str(app_dir))

from logic.date_utils import (
    get_today,
    get_period_boundaries,
    is_date_in_current_period,
    get_days_in_period,
    format_period_label
)


@pytest.mark.unit
class TestGetPeriodBoundaries:
    """Test period boundary calculations for different goal types."""

    # Daily period tests
    def test_daily_period_same_day(self):
        """Daily period should return the same day for start and end."""
        test_date = date(2024, 12, 15)  # Sunday
        start, end = get_period_boundaries('daily', test_date)
        assert start == test_date
        assert end == test_date

    def test_daily_period_different_dates(self):
        """Each day should have its own distinct period."""
        date1 = date(2024, 12, 14)
        date2 = date(2024, 12, 15)

        start1, end1 = get_period_boundaries('daily', date1)
        start2, end2 = get_period_boundaries('daily', date2)

        assert start1 == date1 and end1 == date1
        assert start2 == date2 and end2 == date2
        assert start1 != start2

    # Weekly period tests
    def test_weekly_period_monday(self):
        """Week starting on Monday should have Monday as start."""
        monday = date(2024, 12, 9)  # Monday
        start, end = get_period_boundaries('weekly', monday)

        assert start == monday  # Monday
        assert end == date(2024, 12, 15)  # Sunday
        assert (end - start).days == 6  # 7 days total

    def test_weekly_period_sunday(self):
        """Week ending on Sunday should still start from the same Monday."""
        sunday = date(2024, 12, 15)  # Sunday
        start, end = get_period_boundaries('weekly', sunday)

        assert start == date(2024, 12, 9)  # Monday
        assert end == sunday  # Sunday
        assert (end - start).days == 6

    def test_weekly_period_wednesday(self):
        """Mid-week day should belong to week starting Monday."""
        wednesday = date(2024, 12, 11)  # Wednesday
        start, end = get_period_boundaries('weekly', wednesday)

        assert start == date(2024, 12, 9)  # Monday
        assert end == date(2024, 12, 15)  # Sunday

    def test_weekly_period_same_for_whole_week(self):
        """All days in the same week should return the same period."""
        monday = date(2024, 12, 9)
        expected_start = monday
        expected_end = date(2024, 12, 15)

        for i in range(7):  # Monday through Sunday
            test_date = monday + timedelta(days=i)
            start, end = get_period_boundaries('weekly', test_date)
            assert start == expected_start
            assert end == expected_end

    # Monthly period tests
    def test_monthly_period_first_day(self):
        """First day of month should start the monthly period."""
        first_day = date(2024, 12, 1)
        start, end = get_period_boundaries('monthly', first_day)

        assert start == first_day
        assert end == date(2024, 12, 31)  # Last day of December

    def test_monthly_period_last_day(self):
        """Last day of month should be part of that month's period."""
        last_day = date(2024, 12, 31)
        start, end = get_period_boundaries('monthly', last_day)

        assert start == date(2024, 12, 1)
        assert end == last_day

    def test_monthly_period_mid_month(self):
        """Mid-month day should belong to full month."""
        mid_month = date(2024, 12, 15)
        start, end = get_period_boundaries('monthly', mid_month)

        assert start == date(2024, 12, 1)
        assert end == date(2024, 12, 31)

    def test_monthly_period_february_leap_year(self):
        """February in leap year should have 29 days."""
        feb_leap = date(2024, 2, 15)  # 2024 is a leap year
        start, end = get_period_boundaries('monthly', feb_leap)

        assert start == date(2024, 2, 1)
        assert end == date(2024, 2, 29)  # 29 days in leap year
        assert (end - start).days == 28  # 29 days total (inclusive)

    def test_monthly_period_february_non_leap_year(self):
        """February in non-leap year should have 28 days."""
        feb_non_leap = date(2025, 2, 15)  # 2025 is not a leap year
        start, end = get_period_boundaries('monthly', feb_non_leap)

        assert start == date(2025, 2, 1)
        assert end == date(2025, 2, 28)  # 28 days in non-leap year

    def test_monthly_period_31_day_month(self):
        """31-day months should end on 31st."""
        jan = date(2024, 1, 15)
        start, end = get_period_boundaries('monthly', jan)

        assert start == date(2024, 1, 1)
        assert end == date(2024, 1, 31)

    def test_monthly_period_30_day_month(self):
        """30-day months should end on 30th."""
        april = date(2024, 4, 15)
        start, end = get_period_boundaries('monthly', april)

        assert start == date(2024, 4, 1)
        assert end == date(2024, 4, 30)

    # Year boundary tests
    def test_weekly_period_year_boundary(self):
        """Week spanning year boundary should handle correctly."""
        # Dec 30, 2024 is a Monday
        dec_30 = date(2024, 12, 30)
        start, end = get_period_boundaries('weekly', dec_30)

        assert start == dec_30  # Monday Dec 30
        assert end == date(2025, 1, 5)  # Sunday Jan 5

    def test_monthly_period_december(self):
        """December should correctly calculate last day."""
        dec = date(2024, 12, 15)
        start, end = get_period_boundaries('monthly', dec)

        assert start == date(2024, 12, 1)
        assert end == date(2024, 12, 31)

    def test_monthly_period_january(self):
        """January should correctly calculate after year boundary."""
        jan = date(2025, 1, 15)
        start, end = get_period_boundaries('monthly', jan)

        assert start == date(2025, 1, 1)
        assert end == date(2025, 1, 31)

    # Default reference_date tests
    def test_daily_defaults_to_today(self):
        """When reference_date is None, should use today."""
        start, end = get_period_boundaries('daily')
        today = date.today()

        assert start == today
        assert end == today

    def test_weekly_defaults_to_today(self):
        """Weekly should calculate from today if no reference_date."""
        start, end = get_period_boundaries('weekly')
        today = date.today()

        # Verify today is within the returned period
        assert start <= today <= end
        assert start.weekday() == 0  # Monday

    def test_monthly_defaults_to_today(self):
        """Monthly should calculate from today if no reference_date."""
        start, end = get_period_boundaries('monthly')
        today = date.today()

        assert start.day == 1  # First of month
        assert start <= today <= end
        assert start.month == today.month
        assert end.month == today.month

    # Invalid input tests
    def test_invalid_goal_type_raises_error(self):
        """Invalid goal_type should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid goal_type"):
            get_period_boundaries('yearly', date(2024, 12, 15))

    def test_empty_goal_type_raises_error(self):
        """Empty goal_type should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid goal_type"):
            get_period_boundaries('', date(2024, 12, 15))


@pytest.mark.unit
class TestIsDateInCurrentPeriod:
    """Test checking if a date falls in the current period."""

    def test_today_is_in_daily_period(self):
        """Today should always be in the current daily period."""
        assert is_date_in_current_period(date.today(), 'daily') is True

    def test_yesterday_not_in_daily_period(self):
        """Yesterday should not be in today's daily period."""
        yesterday = date.today() - timedelta(days=1)
        assert is_date_in_current_period(yesterday, 'daily') is False

    def test_tomorrow_not_in_daily_period(self):
        """Tomorrow should not be in today's daily period."""
        tomorrow = date.today() + timedelta(days=1)
        assert is_date_in_current_period(tomorrow, 'daily') is False

    def test_today_in_current_week(self):
        """Today should be in the current week."""
        assert is_date_in_current_period(date.today(), 'weekly') is True

    def test_today_in_current_month(self):
        """Today should be in the current month."""
        assert is_date_in_current_period(date.today(), 'monthly') is True

    def test_date_in_past_week_not_current(self):
        """Date 10 days ago should not be in current weekly period."""
        past_date = date.today() - timedelta(days=10)
        # This might fail if we're at the start of a week, so we go far enough back
        assert is_date_in_current_period(past_date, 'weekly') is False

    def test_date_in_past_month_not_current(self):
        """Date 40 days ago should not be in current monthly period."""
        past_date = date.today() - timedelta(days=40)
        assert is_date_in_current_period(past_date, 'monthly') is False


@pytest.mark.unit
class TestGetDaysInPeriod:
    """Test getting the number of days in a period."""

    def test_daily_period_has_one_day(self):
        """Daily period should always be 1 day."""
        assert get_days_in_period('daily') == 1

    def test_weekly_period_has_seven_days(self):
        """Weekly period should always be 7 days."""
        assert get_days_in_period('weekly') == 7

    def test_monthly_period_current_month(self):
        """Monthly period should return correct days for current month."""
        days = get_days_in_period('monthly')
        today = date.today()

        # Calculate expected days in current month
        start, end = get_period_boundaries('monthly', today)
        expected_days = (end - start).days + 1

        assert days == expected_days

    def test_invalid_goal_type_raises_error(self):
        """Invalid goal_type should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid goal_type"):
            get_days_in_period('yearly')


@pytest.mark.unit
class TestFormatPeriodLabel:
    """Test period label formatting."""

    def test_daily_format(self):
        """Daily format should show day name and date."""
        test_date = date(2024, 12, 15)  # Sunday
        label = format_period_label('daily', test_date)

        # Should contain day name and date info
        assert 'Sunday' in label
        assert 'Dec' in label
        assert '15' in label

    def test_weekly_format(self):
        """Weekly format should show week date range."""
        test_date = date(2024, 12, 11)  # Wednesday (week Dec 9-15)
        label = format_period_label('weekly', test_date)

        assert 'Week of' in label
        assert 'Dec 09' in label or 'Dec 9' in label
        assert '15' in label

    def test_monthly_format(self):
        """Monthly format should show month and year."""
        test_date = date(2024, 12, 15)
        label = format_period_label('monthly', test_date)

        assert 'December' in label
        assert '2024' in label

    def test_format_defaults_to_today(self):
        """Format functions should work without reference_date."""
        # Should not raise errors
        daily_label = format_period_label('daily')
        weekly_label = format_period_label('weekly')
        monthly_label = format_period_label('monthly')

        assert len(daily_label) > 0
        assert len(weekly_label) > 0
        assert len(monthly_label) > 0

    def test_invalid_goal_type_raises_error(self):
        """Invalid goal_type should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid goal_type"):
            format_period_label('yearly', date(2024, 12, 15))


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_leap_year_detection(self):
        """Test that leap years are handled correctly."""
        # 2024 is a leap year
        feb_29_2024 = date(2024, 2, 29)
        start, end = get_period_boundaries('monthly', feb_29_2024)
        assert end == feb_29_2024

        # 2025 is not a leap year
        feb_28_2025 = date(2025, 2, 28)
        start, end = get_period_boundaries('monthly', feb_28_2025)
        assert end == feb_28_2025

    def test_century_leap_year(self):
        """Test century years (2000 was leap, 1900 was not)."""
        # 2000 was a leap year (divisible by 400)
        feb_2000 = date(2000, 2, 15)
        start, end = get_period_boundaries('monthly', feb_2000)
        assert end == date(2000, 2, 29)

    def test_week_at_year_start(self):
        """Test week calculation at start of year."""
        jan_1_2024 = date(2024, 1, 1)  # Monday
        start, end = get_period_boundaries('weekly', jan_1_2024)

        assert start == jan_1_2024
        assert end == date(2024, 1, 7)

    def test_week_at_year_end(self):
        """Test week calculation at end of year."""
        dec_31_2024 = date(2024, 12, 31)  # Tuesday
        start, end = get_period_boundaries('weekly', dec_31_2024)

        # Should start on Monday Dec 30
        assert start == date(2024, 12, 30)
        # Should end on Sunday Jan 5, 2025
        assert end == date(2025, 1, 5)

    def test_very_old_date(self):
        """Test that old dates work correctly."""
        old_date = date(1900, 1, 1)
        start, end = get_period_boundaries('daily', old_date)
        assert start == old_date
        assert end == old_date

    def test_far_future_date(self):
        """Test that future dates work correctly."""
        future_date = date(2099, 12, 31)
        start, end = get_period_boundaries('monthly', future_date)
        assert start == date(2099, 12, 1)
        assert end == future_date
