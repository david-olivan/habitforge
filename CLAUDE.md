# Claude Code Memory File - HabitForge Project

## Project Context
HabitForge is a privacy-focused, offline-first habit tracking application for Android built with Python and Kivy.

## Current Project State (December 10, 2024)

### Directory Structure
```
habitforge/
├── .claude/                    # Claude configuration
│   └── claude-commit-guidelines.md
├── .github/                    # GitHub workflows
├── app/                        # Main application code
│   ├── assets/                 # Icons, images
│   ├── components/             # Reusable UI components
│   │   ├── __init__.py
│   │   ├── color_picker.py     # HabitColorPicker component
│   │   └── habit_card.py       # HabitCard widget for habit list
│   ├── config/                 # Configuration
│   │   ├── __init__.py
│   │   └── constants.py        # App constants and color palette
│   ├── data/                   # Database files (created at runtime)
│   │   └── habitforge.db       # SQLite database
│   ├── logic/                  # Business logic
│   │   ├── __init__.py
│   │   ├── habit_manager.py    # Habit validation and business rules
│   │   ├── date_utils.py       # Date calculation utilities
│   │   └── completion_manager.py # Completion tracking logic
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── schema.sql          # Database schema reference
│   │   ├── schemas.py          # Pydantic models (Habit, Completion)
│   │   └── database.py         # Database CRUD operations
│   ├── utils/                  # Utilities (only __init__.py)
│   ├── views/                  # UI screens
│   │   ├── __init__.py
│   │   ├── habit_form.py       # Habit create/edit form
│   │   └── main_screen.py      # Main habit list screen
│   └── main.py                 # Entry point - KivyMD app with ScreenManager
├── docs/                       # Documentation
│   └── PRD_HabitTracker.md    # Product Requirements Document
├── scripts/                    # Build/utility scripts
├── tests/                      # Test files
├── buildozer.spec             # Android build configuration
├── requirements.txt           # Python dependencies
├── requirements-app.txt       # App-specific dependencies
├── README.md                  # Main documentation
├── TechDebt.md               # Technical debt tracking
└── LICENSE
```

### Current Implementation Status

✅ **PRD Section 2.1.1 - Habit Management: COMPLETED**
✅ **PRD Section 2.1.2 - Completion Tracking: COMPLETED**
✅ **PRD Section 2.1.3 - Habit List Display: COMPLETED**
✅ **PRD Section 2.1.4 - Data Persistence: COMPLETED**
✅ **PRD Section 2.2.1 - Streak Tracking: COMPLETED**

🎉 **MVP PHASE 1 COMPLETE** - All vital features implemented!
🔥 **PHASE 2 STARTED** - Streak tracking feature complete!

**Implemented Files:**

**Data Layer:**
- ✅ [app/models/schema.sql](app/models/schema.sql) - Complete database schema with habits, completions, settings tables
- ✅ [app/models/schemas.py](app/models/schemas.py) - Pydantic models (Habit, Completion)
- ✅ [app/models/database.py](app/models/database.py) - SQLite CRUD operations with context managers

**Business Logic:**
- ✅ [app/logic/habit_manager.py](app/logic/habit_manager.py) - Habit validation and business rules
- ✅ [app/logic/date_utils.py](app/logic/date_utils.py) - Date period calculations (daily/weekly/monthly)
- ✅ [app/logic/completion_manager.py](app/logic/completion_manager.py) - Completion tracking and progress calculation
- ✅ [app/logic/streak_calculator.py](app/logic/streak_calculator.py) - Streak calculation (consecutive periods of goal completion)

**UI Components:**
- ✅ [app/components/color_picker.py](app/components/color_picker.py) - HabitColorPicker widget (4×2 grid)
- ✅ [app/components/habit_card.py](app/components/habit_card.py) - HabitCard widget with progress display

**Views/Screens:**
- ✅ [app/views/habit_form.py](app/views/habit_form.py) - Habit create/edit form with navigation
- ✅ [app/views/main_screen.py](app/views/main_screen.py) - Main screen with habit list grouped by type

**Configuration:**
- ✅ [app/config/constants.py](app/config/constants.py) - Color palette (8 colors) and validation constants
- ✅ [app/main.py](app/main.py) - App entry point with ScreenManager navigation

**Functionality Implemented:**

**Habit Management (2.1.1):**
- ✅ Create new habits with name, color, goal type, and goal count
- ✅ Update existing habits (edit mode)
- ✅ Database persistence with SQLite
- ✅ Data validation using Pydantic models
- ✅ Case-insensitive unique name constraint
- ✅ Color picker with visual selection feedback
- ✅ Goal type dropdown (Daily, Weekly, Monthly)
- ✅ Goal count with +/- buttons (1-100 range)
- ✅ Real-time validation error display
- ✅ Success messages with auto-reset
- ✅ Archive/unarchive habits (soft delete)
- ✅ Hard delete habits

**Completion Tracking (2.1.2):**
- ✅ Increment completion count with + button
- ✅ Progress calculation for daily/weekly/monthly goals
- ✅ Visual progress display (X / Y format)
- ✅ Goal met indicator (✓ checkmark)
- ✅ Date period boundary calculations
- ✅ Main screen with habit list grouped by type
- ✅ HabitCard component with colored bar and progress
- ✅ Screen navigation (Main ↔ Form)
- ✅ Automatic list refresh after habit save
- ✅ Completions table with UPSERT operations
- ✅ Foreign key CASCADE delete

**Streak Tracking (2.2.1):**
- ✅ Calculate consecutive periods with goal met (backward walking algorithm)
- ✅ Exclude current period from streak count until complete
- ✅ Display flame icon (🔥) on HabitCard next to progress
- ✅ Grey icon for no streak (0), pale orange for active streak (>0)
- ✅ On-demand calculation (no database storage, zero migration risk)
- ✅ Handles daily, weekly, and monthly goal types correctly
- ✅ Streak breaks naturally at first incomplete period

**Testing Status:**
- ⏸️ Not yet tested (implementation complete, awaiting testing)

### Technology Stack
- **Language**: Python 3.11 (NOT 3.12 - p4a compatibility)
- **UI Framework**: Kivy 2.3.1, KivyMD 1.2.0 (Material Design 3)
- **Validation**: Native Python validation (Pydantic removed - build compatibility)
- **Database**: SQLite3 with context managers
- **Build Tool**: Buildozer 1.5.0+
- **Target Platform**: Android 7.0+ (API Level 24), Target API 35 (2025 compliance)
- **Android NDK**: 26b (16KB page size support)
- **Date/Time**: python-dateutil 2.9.0

## Android Build Learnings (December 10, 2024)

### Critical Build Fixes - v0.1.3

**Problem**: APK crashed immediately after splash screen with no error message.

**Root Cause Analysis**:
1. **Missing KivyMD Dependencies**: KivyMD 1.2.0 requires `filetype` and `pillow` modules that weren't in requirements
2. **Python 3.10+ Type Hints**: Used `int | None` syntax incompatible with Python 3.11 on Android
3. **Window.size on Android**: Setting Window.size causes issues on mobile platforms

**Solutions Applied**:
1. **Added Missing Dependencies** to `requirements-app.txt` and `buildozer.spec`:
   - `filetype==1.2.0` - **Critical**: KivyMD import dependency
   - `pillow==10.4.0` - Image processing for KivyMD
   - `certifi`, `charset-normalizer`, `idna` - SSL/HTTP support
   - `requests`, `urllib3`, `six` - Network and compatibility libraries

2. **Fixed Type Hints** in [app/logic/habit_manager.py](app/logic/habit_manager.py):
   ```python
   # OLD (Python 3.10+ only):
   def check_unique_name(name: str, exclude_id: int | None = None) -> bool:

   # NEW (Python 3.11 compatible):
   from typing import Optional
   def check_unique_name(name: str, exclude_id: Optional[int] = None) -> bool:
   ```

3. **Platform-Specific Window Config** in [app/main.py](app/main.py):
   ```python
   from kivy.utils import platform
   if platform not in ('android', 'ios'):
       Window.size = (400, 700)  # Desktop only
   ```

### 2025 Google Play Compliance Updates

**Buildozer.spec Configuration**:
- `android.api = 35` - Target API 35 (Android 15) - Required by August 31, 2025
- `android.sdk = 35` - SDK version 35
- `android.ndk = 26b` - NDK r26+ for 16KB page size support (deadline: Nov 1, 2025)
- `android.minapi = 24` - Minimum Android 7.0
- `android.arch = arm64-v8a` - 64-bit architecture

### Dependency Management Best Practice

**Use `pip freeze` for exact versions**:
```powershell
python -m pip freeze > pip-freeze.txt
```
Then manually filter for app dependencies (exclude Windows-specific packages like `kivy-deps.*`, `pywin32`, build tools like `buildozer`, `virtualenv`).

**Files to keep in sync**:
- `requirements.txt` - Desktop development dependencies
- `requirements-app.txt` - Android APK runtime dependencies (no build tools, no Windows packages)
- `buildozer.spec` requirements line - Must match requirements-app.txt

### Debugging APK Crashes

**Get Android logs via ADB**:
```bash
adb logcat | grep -i python  # Linux/Mac
adb logcat > logs.txt  # Windows (then search for 'python' or 'ModuleNotFoundError')
```

**Common crash patterns**:
- `ModuleNotFoundError` - Missing dependency in requirements
- Silent crash after KivyMD init - Usually missing KivyMD dependencies
- Type errors - Check Python 3.10+ syntax compatibility

### Python Version Constraints

**MUST use Python 3.11** (not 3.12):
- python-for-android doesn't fully support Python 3.12 yet
- Use `typing.Optional[T]` instead of `T | None` for type hints
- Test locally with Python 3.11 before building APK

## Critical Instructions

### ⚠️ NEVER COMMIT UNLESS EXPLICITLY DIRECTED
**IMPORTANT**: Do NOT create git commits automatically. Only commit when the user explicitly asks for it.

When committing (if requested), use the guidelines in [.claude/claude-commit-guidelines.md](.claude/claude-commit-guidelines.md):
- Follow Conventional Commits format: `<type>(<scope>): <subject>`
- Types: feat, fix, docs, style, refactor, perf, test, chore, ci
- Scopes: habits, ui, database, analytics, build, ci
- Use imperative mood, lowercase, max 50 chars, no period
- Example: `feat(database): add habit schema and CRUD operations`

## Implementation Details

### Database Schema
Complete schema documented in [app/models/schema.sql](app/models/schema.sql)

**Habits Table:**
```sql
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    color TEXT NOT NULL,
    goal_type TEXT NOT NULL CHECK(goal_type IN ('daily', 'weekly', 'monthly')),
    goal_count INTEGER NOT NULL CHECK(goal_count > 0 AND goal_count <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived INTEGER DEFAULT 0,
    UNIQUE(name COLLATE NOCASE)
);
```

**Completions Table:**
```sql
CREATE TABLE IF NOT EXISTS completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date DATE NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    UNIQUE(habit_id, date)
);
```

**Indexes:**
- `idx_completions_habit_date` - Composite index on (habit_id, date)
- `idx_habits_archived` - Index on archived column

### Pydantic Models
Defined in [app/models/schemas.py](app/models/schemas.py):

**Habit Models:**
- **HabitBase**: Base model with validation
  - `name`: 1-50 chars, stripped whitespace
  - `color`: Hex pattern `#RRGGBB`
  - `goal_type`: Literal['daily', 'weekly', 'monthly']
  - `goal_count`: Integer 1-100
- **HabitCreate**: Inherits HabitBase, all fields required
- **HabitUpdate**: All fields optional for partial updates
- **Habit**: Complete model with `id`, `created_at`, `archived` fields

**Completion Models:**
- **CompletionBase**: Base model with validation
  - `habit_id`: Positive integer
  - `date`: Date (not in future)
  - `count`: Non-negative integer
- **CompletionCreate**: Inherits CompletionBase
- **Completion**: Complete model with `id`, `completed_at` fields

### Color Palette
8 Material Design colors defined in [app/config/constants.py](app/config/constants.py):
- `#E57373` (Red), `#FFB74D` (Orange), `#FFF176` (Yellow), `#81C784` (Green)
- `#4DB6AC` (Teal), `#64B5F6` (Blue), `#BA68C8` (Purple), `#F06292` (Pink)

### Key Design Decisions
1. **Pydantic for Validation**: Automatic field validation with clear error messages
2. **Context Managers**: Safe database connection handling
3. **Soft Delete**: Archive flag instead of hard delete (preserves data integrity)
4. **Material Design 3**: KivyMD components for modern Android UI
5. **Cross-Platform Paths**: Handles Android `user_data_dir` and desktop fallback
6. **Component Naming**: `HabitColorPicker` to avoid Kivy built-in conflicts
7. **UPSERT Pattern**: Efficient completion increment using SQLite ON CONFLICT
8. **Period Calculations**: Separate date_utils module for reusable date logic
9. **ScreenManager Navigation**: Clean separation between main list and form screens
10. **Relative Imports**: All imports within `app/` use relative paths (e.g., `from models.database` NOT `from app.models.database`) since the app is run from the `app/` directory
11. **Pydantic Field Naming**: Avoid naming model fields the same as their type (e.g., use `date: DateType` not `date: date`) to prevent schema generation issues
12. **FloatLayout for FAB**: Use FloatLayout to allow FAB to truly float above scrollable content instead of taking up layout space in MDBoxLayout

## Current Task
**IN PLANNING: PRD Section 2.2.2 - Calendar Heatmap Visualization** 🔄

Planning GitHub-style calendar heatmap for each habit showing completion patterns:
- 🔄 GitHub-style grid with color intensity based on completion percentage
- 🔄 Per-habit heatmaps using assigned habit colors
- 🔄 Week/Month/Year view switcher
- 🔄 Date navigation (Previous/Next/Today buttons)
- 🔄 Current date indicator
- 🔄 Zero database schema changes (read-only queries)
- 🔄 Material Design 3 aesthetic

**Planned Implementation:**
- New file: [app/components/heatmap_cell.py](app/components/heatmap_cell.py) - Canvas-based cell widget
- New file: [app/components/heatmap_grid.py](app/components/heatmap_grid.py) - Grid layout with dimension logic
- New file: [app/logic/heatmap_data.py](app/logic/heatmap_data.py) - Data transformation and caching
- Replace: [app/views/analytics_content.py](app/views/analytics_content.py) - Main screen with heatmaps

**Previously Completed Tasks:**
- ✅ Section 2.2.1: Streak Tracking (consecutive period tracking with flame icon)

**Next Potential Tasks** (from PRD, not started):
- Section 2.2.3: Week Navigation
- Section 2.2.4: Collapsible Sections
- Section 2.2.5: Progress Statistics

## Known Issues
- KivyMD 1.2.0 shows deprecation warning (version 2.0.0 available but not yet installed)
- No confirmation dialog for deletions
- No unit tests yet
- Implementation not yet tested (code complete, testing pending)
- Empty state on main screen needs testing
- Error handling with Snackbar/Toast not implemented (uses logging only)

## Notes
- This is MVP Phase 1 work
- Focus on essential functionality only
- Keep code simple and maintainable
- Follow the project structure defined in README.md and PRD
- Database created at runtime in `app/data/habitforge.db`
- Foreign key constraints enabled via PRAGMA

---
*Last Updated: December 10, 2024*