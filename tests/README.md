# HabitForge Test Suite

## Overview

This test suite provides comprehensive coverage of HabitForge's core business logic and data layer. The tests are designed to be **fast, reliable, and runnable without UI dependencies**, making them perfect for continuous verification during development.

## Test Statistics

**Total: 85 Unit Tests (All Passing ✅)**
- Date utilities: 43 tests
- Database operations: 42 tests

**Execution Time: ~0.24 seconds** ⚡

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and test infrastructure
├── pytest.ini                     # Pytest configuration (in project root)
├── unit/                          # Unit tests (no external dependencies)
│   ├── logic/
│   │   └── test_date_utils.py    # 43 tests - Period calculations
│   └── models/
│       └── test_database.py      # 42 tests - CRUD operations
├── integration/                   # Integration tests (future)
├── test_android_compatibility.py # Android build compatibility
├── test_buildozer_spec.py        # Build configuration validation
└── test_streak_calculator.py     # Streak tracking (legacy)
```

## What's Tested

### ✅ Date Utilities (logic/date_utils.py) - 43 tests

**Period Boundaries:**
- Daily, weekly, monthly period calculations
- Week boundaries (Monday-Sunday)
- Month boundaries (handling 28/29/30/31 days)
- Year boundaries and edge cases
- Leap year handling (including century rules)

**Date Validation:**
- Current period detection
- Days in period calculations
- Period label formatting

**Edge Cases:**
- Very old dates (1900)
- Year transitions
- February in leap/non-leap years
- Invalid input handling

### ✅ Database Operations (models/database.py) - 42 tests

**Habit CRUD:**
- Create habits with validation
- Read all habits (with/without archived)
- Read single habit by ID
- Update habit fields (single & multiple)
- Delete habits (hard delete)
- Archive/unarchive habits (soft delete)
- Foreign key cascade deletes

**Completion Tracking:**
- Increment completions (UPSERT pattern)
- Decrement completions (min 0)
- Get completion for specific date
- Get completions for habit (with date range filtering)
- Get completions across all habits

**Settings:**
- Get/set individual settings
- Get all settings
- UPSERT behavior

**Database Constraints:**
- Unique habit names (case-insensitive)
- Goal type CHECK constraint
- Goal count range CHECK (1-100)
- Completion uniqueness per date

**Edge Cases:**
- Special characters in names
- Historical dates
- Empty result sets
- Reversed date ranges

## How to Run Tests

### Run All Unit Tests
```bash
pytest tests/unit/ -v
```

### Run Specific Test Module
```bash
# Date utilities only
pytest tests/unit/logic/test_date_utils.py -v

# Database operations only
pytest tests/unit/models/test_database.py -v
```

### Run Tests by Marker
```bash
# Run only database tests
pytest -m database -v

# Run only unit tests
pytest -m unit -v
```

### Run with Coverage Report
```bash
pytest tests/unit/ --cov=app/logic --cov=app/models --cov-report=term-missing
```

### Run Fast (Parallel Execution)
```bash
pytest tests/unit/ -n auto  # Requires pytest-xdist
```

## Test Infrastructure

### Fixtures (conftest.py)

**Database Fixtures:**
- `test_db` - Fresh in-memory SQLite database per test
- `create_test_habit(...)` - Factory for creating test habits
- `create_test_completion(...)` - Factory for creating test completions

**Data Fixtures:**
- `sample_habit_data` - Valid habit dictionary
- `sample_habits_data` - Multiple habit examples
- `mock_today()` - Function to mock current date

**Utilities:**
- `generate_date_range()` - Generate date sequences
- `get_test_date()` - Get relative dates (e.g., 7 days ago)

### Mocking Strategy

**Kivy Logger Mock:**
All tests mock `kivy.logger.Logger` to avoid Kivy runtime dependency. Tests run in plain Python without UI framework.

**Database Connection Mock:**
Tests use `unittest.mock.patch` to replace `database.get_connection()` with in-memory SQLite database, ensuring:
- Fast execution (no disk I/O)
- Isolation (no shared state between tests)
- No cleanup needed (database destroyed after test)

## Test Design Principles

1. **Fast:** All 85 tests run in <0.25 seconds
2. **Isolated:** Each test uses fresh database
3. **Deterministic:** No flaky tests, 100% reproducible
4. **Comprehensive:** Edge cases, error conditions, constraints
5. **Readable:** Clear test names describe what's tested
6. **Maintainable:** DRY fixtures, organized by feature

## Running Tests in CI/CD

These tests are perfect for continuous integration:

```bash
# In GitHub Actions / GitLab CI
python -m pytest tests/unit/ -v --tb=short --maxfail=1
```

**Exit codes:**
- 0: All tests passed ✅
- 1: At least one test failed ❌

## Coverage Goals

**Current Coverage:**
- `logic/date_utils.py`: ~95%+ (comprehensive)
- `models/database.py`: ~90%+ (all CRUD operations)

**Target Coverage:**
- Core business logic: 90%+
- Data layer: 85%+
- UI components: 20-30% (basic instantiation only)

## Future Test Additions

**Pending Unit Tests:**
- [ ] `logic/habit_manager.py` - Validation logic
- [ ] `logic/completion_manager.py` - Progress calculations
- [ ] `logic/heatmap_data.py` - Heatmap generation
- [ ] `logic/data_manager.py` - Import/export

**Pending Integration Tests:**
- [ ] End-to-end habit workflows
- [ ] Data import/export integrity
- [ ] Multi-habit scenarios

## Troubleshooting

### Tests fail with "ModuleNotFoundError"
```bash
pip install pytest python-dateutil
```

### Tests fail with "no such table"
Check that `conftest.py` creates all required tables (habits, completions, settings).

### Kivy import errors
Tests should mock Kivy. Check `conftest.py` has:
```python
sys.modules['kivy.logger'] = ...
```

## Best Practices

**When adding new tests:**
1. Use existing fixtures from `conftest.py`
2. Mock external dependencies (Kivy, file I/O)
3. Test both success and error cases
4. Add descriptive docstrings
5. Run tests before committing

**Test naming:**
- `test_<action>_<condition>` (e.g., `test_create_habit_success`)
- Be specific: `test_update_habit_nonexistent` not `test_update_fails`

**Assertions:**
- Use specific assertions: `assert x == 5` not `assert x`
- Add helpful messages: `assert len(habits) == 2, f"Expected 2 habits, got {len(habits)}"`

## Maintenance

Run tests frequently during development:
```bash
# Watch mode (requires pytest-watch)
ptw tests/unit/

# Run on file save
pytest-watch tests/unit/
```

Keep tests fast:
- Avoid real disk I/O (use in-memory DB)
- Don't sleep() unless testing timing
- Mock expensive operations

---

**Last Updated:** January 15, 2026
**Test Count:** 85 passing
**Coverage:** ~85% of core business logic
