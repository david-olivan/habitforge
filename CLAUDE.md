# Claude Code Memory File - HabitForge Project

## Project Context
HabitForge is a privacy-focused, offline-first habit tracking application for Android built with Python and Kivy.

## Current Project State (December 8, 2024)

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
│   │   └── color_picker.py     # HabitColorPicker component
│   ├── config/                 # Configuration
│   │   ├── __init__.py
│   │   └── constants.py        # App constants and color palette
│   ├── data/                   # Database files (created at runtime)
│   │   └── habitforge.db       # SQLite database
│   ├── logic/                  # Business logic
│   │   ├── __init__.py
│   │   └── habit_manager.py    # Habit validation and business rules
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── schema.sql          # Database schema reference
│   │   ├── schemas.py          # Pydantic models
│   │   └── database.py         # Database CRUD operations
│   ├── utils/                  # Utilities (only __init__.py)
│   ├── views/                  # UI screens
│   │   ├── __init__.py
│   │   └── habit_form.py       # Habit create/edit form
│   └── main.py                 # Entry point - KivyMD app
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

**Implemented Files:**
- ✅ [app/models/schema.sql](app/models/schema.sql) - Complete database schema with habits, completions, settings tables
- ✅ [app/models/schemas.py](app/models/schemas.py) - Pydantic models (HabitBase, HabitCreate, HabitUpdate, Habit)
- ✅ [app/models/database.py](app/models/database.py) - SQLite CRUD operations with context managers
- ✅ [app/config/constants.py](app/config/constants.py) - Color palette (8 colors) and validation constants
- ✅ [app/logic/habit_manager.py](app/logic/habit_manager.py) - Business logic with unique name checking
- ✅ [app/components/color_picker.py](app/components/color_picker.py) - HabitColorPicker widget (4×2 grid)
- ✅ [app/views/habit_form.py](app/views/habit_form.py) - Complete habit form with validation
- ✅ [app/main.py](app/main.py) - Updated to KivyMD with database initialization

**Functionality Implemented:**
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

**Testing Status:**
- ✅ Successfully created test habit "David" with green color, weekly goal
- ✅ Database operations confirmed working
- ✅ Validation working correctly
- ✅ UI form functional on desktop

### Technology Stack
- **Language**: Python 3.9+
- **UI Framework**: Kivy 2.3.1, KivyMD 1.2.0 (Material Design 3)
- **Validation**: Pydantic 2.5.3
- **Database**: SQLite3 with context managers
- **Build Tool**: Buildozer 1.5.0+
- **Target Platform**: Android 7.0+ (API Level 24)
- **Date/Time**: python-dateutil 2.9.0

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
    UNIQUE(name COLLATE NOCASE)  -- Case-insensitive unique constraint
);
```

**Completions Table** (for future use):
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

### Pydantic Models
Defined in [app/models/schemas.py](app/models/schemas.py):

- **HabitBase**: Base model with validation
  - `name`: 1-50 chars, stripped whitespace
  - `color`: Hex pattern `#RRGGBB`
  - `goal_type`: Literal['daily', 'weekly', 'monthly']
  - `goal_count`: Integer 1-100

- **HabitCreate**: Inherits HabitBase, all fields required
- **HabitUpdate**: All fields optional for partial updates
- **Habit**: Complete model with `id`, `created_at`, `archived` fields

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

## Current Task
**No active task.** Section 2.1.1 implementation is complete.

**Next Potential Tasks** (from PRD, not started):
- Section 2.1.2: Habit Completion Tracking
- Section 2.1.3: Habit List Display
- Main screen navigation with ScreenManager
- Streak calculation logic
- Analytics and reports

## Known Issues
- KivyMD 1.2.0 shows deprecation warning (version 2.0.0 available but not yet installed)
- No navigation system yet (form is the only screen)
- No confirmation dialog for deletions
- No unit tests yet

## Notes
- This is MVP Phase 1 work
- Focus on essential functionality only
- Keep code simple and maintainable
- Follow the project structure defined in README.md and PRD
- Database created at runtime in `app/data/habitforge.db`

---
*Last Updated: December 8, 2024*