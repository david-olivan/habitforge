# Technical Debt & Future Tasks

This file tracks technical debt, deferred tasks, and future improvements for HabitForge.

**Last Updated:** January 10, 2026 (v0.2.0)
**Next Review:** After internal testing feedback

---

## ⚠️ CRITICAL: Testing Gap

### Automated Test Suite Required

**Status:** ⚠️ **NOT IMPLEMENTED** - All functionality has been manually tested only

**Priority:** HIGH - Must be addressed before production release

All features listed below as "✅ Completed" have been manually tested on real devices but **lack automated test coverage**. This creates significant risk for:
- Regression bugs during future development
- Undetected edge cases
- Difficult refactoring
- Time-consuming manual QA for each release

### Required Test Coverage

**Unit Tests Needed:**
- ✅ Habit CRUD operations (create, read, update, archive, hard delete)
  - Test database operations with SQLite
  - Test unique name constraint (case-insensitive)
  - Test validation rules (name length, color format, goal ranges)

- ✅ Completion tracking and progress calculations
  - Test increment operations with UPSERT logic
  - Test daily/weekly/monthly goal progress calculation
  - Test foreign key CASCADE delete behavior

- ✅ Streak calculation logic
  - Test consecutive period tracking (backward walking algorithm)
  - Test period boundary edge cases (week start/end, month transitions)
  - Test incomplete current period exclusion
  - Test streak breaks at first incomplete period

- ✅ Heatmap data generation
  - Test completion percentage calculations
  - Test date range queries (week/month/year views)
  - Test color intensity mapping (0-100%)

- ✅ Date navigation and period calculations
  - Test date_utils functions (get_week_boundaries, get_month_boundaries)
  - Test timezone handling with python-dateutil
  - Test edge cases (leap years, month boundaries, DST transitions)

- ✅ Data import/export functionality
  - Test CSV export with proper formatting
  - Test JSON import with validation
  - Test error handling for corrupted files

- ✅ Localization (i18n)
  - Test string loading for English and Spanish
  - Test fallback behavior for missing translations
  - Test string formatting with parameters

- ✅ Database schema integrity
  - Test foreign key constraints
  - Test CASCADE delete behavior
  - Test unique constraints (habit name case-insensitive)
  - Test index creation and query performance

**Integration Tests Needed:**
- End-to-end user workflows (create habit → log completion → view analytics)
- Navigation between screens
- Data persistence across app restarts
- Language switching

**UI Tests Needed:**
- Widget rendering (HabitCard, HeatmapGrid, ColorPicker)
- Form validation error display
- Button interactions
- Screen transitions

**Testing Framework Recommendations:**
- **pytest** - Python unit testing
- **pytest-cov** - Code coverage reporting
- **unittest.mock** - Mocking database and file I/O
- Target: 80%+ code coverage before production

---

## Build & Deployment

### Android Build Testing
- [x] **✅ Test first Docker-based APK build**
  - Status: ✅ **COMPLETED** (v0.1.3)
  - Tested: Successful build and installation on real device
  - Build time: First build ~45 minutes, subsequent builds ~8 minutes
  - Output: `bin/habitforge-0.2.0-arm64-v8a-debug.apk`

- [x] **✅ Install and test APK on physical Android device**
  - Status: ✅ **COMPLETED** (v0.1.3)
  - Method: ADB install via USB debugging
  - Result: App runs successfully, all features functional
  - Fixed: Missing KivyMD dependencies (filetype, pillow)
  - Fixed: Python 3.10+ type hint compatibility (Optional[T] instead of T | None)

### AAB Bundle for Google Play
- [ ] **Build AAB release bundle**
  - Status: ⏸️ **IN PROGRESS** (v0.2.0)
  - Priority: High
  - Script: `scripts/build_android_aab.sh` (WSL/bash)
  - Output: `bin/habitforge-0.2.0-release.aab`
  - Uses Google Play App Signing (no manual keystore needed)

### App Icon
- [x] **✅ Convert SVG icons to PNG format**
  - Status: ✅ **COMPLETED**
  - Format: PNG (512x512 for store, multiple sizes for app)
  - Location: `app/assets/icons/icon.png`, `presplash.png`
  - Configured in buildozer.spec

### Release Build
- [x] **✅ Configure signing for release AAB**
  - Status: ✅ **COMPLETED** (using Google Play App Signing)
  - Method: Google Play Console manages app signing key
  - Developer manages: Upload key only (handled by buildozer)
  - Security: Google manages signing certificate securely
  - Recovery: Upload key can be reset if compromised

---

## Phase 1: MVP Implementation ✅ **COMPLETED**

### Database Layer ✅
- [x] **✅ Implement `models/database.py`**
  - SQLite connection management with context managers
  - Table creation (habits, completions, settings)
  - CRUD operations with Pydantic validation
  - Foreign key constraints enabled

- [x] **✅ Implement `models/schemas.py`**
  - Pydantic models (HabitBase, HabitCreate, HabitUpdate, Habit)
  - Completion models (CompletionBase, CompletionCreate, Completion)
  - Type hints and field validation
  - Field validators for dates, colors, name lengths

### Business Logic ✅
- [x] **✅ Implement `logic/habit_manager.py`**
  - Habit CRUD operations with validation
  - Unique name constraint checking (case-insensitive)
  - Archive/unarchive functionality (soft delete)
  - Hard delete with CASCADE cleanup

- [x] **✅ Implement `logic/completion_manager.py`**
  - Completion tracking with UPSERT logic
  - Progress calculation (daily/weekly/monthly)
  - Goal met detection
  - Date period boundary handling

- [x] **✅ Implement `logic/date_utils.py`**
  - Week boundaries (Monday-Sunday)
  - Month boundaries (first/last day of month)
  - Date formatting helpers
  - Period boundary calculations

- [x] **✅ Implement `logic/streak_calculator.py`**
  - Consecutive period completion tracking (backward walking)
  - Exclude incomplete current period
  - Handle daily/weekly/monthly goal types
  - Zero-migration on-demand calculation

### Configuration ✅
- [x] **✅ Implement `config/constants.py`**
  - 8-color Material Design palette
  - Validation constants (name length, goal ranges)
  - App-wide configuration

### UI Layer ✅
- [x] **✅ Enhance `app/main.py`**
  - KivyMD Material Design 3 theme
  - Database initialization
  - ScreenManager navigation
  - Bottom navigation tabs (Habits, Analytics, Account)

- [x] **✅ Implement `views/main_screen.py`**
  - Habit list with grouping (Daily/Weekly/Monthly)
  - Collapsible sections with chevron toggles
  - Floating Action Button (FAB) for add habit
  - Real-time refresh on data changes

- [x] **✅ Implement `views/habit_form.py`**
  - Text input for habit name with validation
  - Color picker (HabitColorPicker component)
  - Goal type dropdown (Daily/Weekly/Monthly)
  - Goal count with +/- buttons (1-100 range)
  - Save/Cancel buttons with navigation
  - Edit mode vs Create mode (dynamic UI)

- [x] **✅ Implement `components/habit_card.py`**
  - Habit display widget with colored bar
  - Progress display (X / Y format)
  - Increment button (+ button)
  - Goal completion indicator (✓ checkmark)
  - Streak flame icon (🔥) with color coding
  - Tap-to-edit interaction

- [x] **✅ Implement `components/color_picker.py`**
  - HabitColorPicker widget (4×2 grid)
  - Visual selection feedback
  - Material Design color palette

---

## Phase 2: Core Features ✅ **MOSTLY COMPLETED**

- [x] **✅ Implement streak calculation**
  - Consecutive period completion tracking
  - Visual indicator (flame icon 🔥)
  - Color coding: grey (0 streak), pale orange (active streak)
  - Pending streak display before period completion

- [x] **✅ Implement collapsible sections**
  - Expandable/collapsible habit groups (Daily/Weekly/Monthly)
  - Chevron icon rotation (down ↔ right)
  - Independent state per section
  - Smooth dynamic rendering
  - **Future enhancement**: Persist collapsed state in settings table across app sessions

- [ ] **⏸️ Implement week navigation** (PRD Section 2.2.3)
  - Status: ⏸️ **NOT STARTED**
  - Priority: Medium
  - Features needed:
    - 5-day date navigation strip
    - Current day highlight
    - Navigate to past/future dates
    - Log completions for specific dates
  - **Note**: Currently have date navigation in Analytics tab, but not main Habits tab

- [x] **✅ Add edit/archive functionality**
  - Tap card to edit habit
  - Edit form with pre-filled data
  - Archive button in edit form (soft delete)
  - Success messages and navigation
  - **Future enhancement**: View/restore archived habits screen (separate screen or toggle filter)

- [x] **✅ Calendar heatmap visualization** (PRD Section 2.2.2)
  - GitHub-style heatmap grid
  - Color intensity based on completion % (0-100%)
  - Week/Month/Year view switcher
  - Date navigation (Previous/Next/Today buttons)
  - Current date indicator with border
  - Per-habit heatmaps using habit colors
  - Month view alignment fixed (weekday columns correct)

- [x] **✅ Data import/export**
  - CSV export functionality
  - JSON import functionality
  - Dedicated import/delete data screens
  - File picker integration

- [x] **✅ Localization (i18n)**
  - English and Spanish translations
  - LocalizationManager with JSON files
  - Language preference persistence
  - `_()` helper function for strings

---

## Phase 3: Analytics ⏸️ **PARTIALLY COMPLETED**

- [x] **✅ Implement reports screen**
  - Tab navigation (Analytics bottom nav item)
  - Heatmap view switcher (Week/Month/Year)
  - Date range selector
  - Real-time refresh with smart caching

- [x] **✅ Implement calendar heatmap**
  - Color intensity based on completion %
  - Interactive grid layout
  - Per-habit heatmaps

- [ ] **⏸️ Add export functionality**
  - Status: ⏸️ **DEFERRED**
  - Priority: Low
  - Features:
    - Save heatmap as PNG image
    - Share via Android intent
  - **Note**: Data export (CSV) already implemented, but visual heatmap export not yet done

---

## Code Quality

- [ ] **Add type hints throughout codebase**
  - Status: ⏸️ **PARTIAL** - Some modules have type hints (habit_manager, schemas)
  - Priority: Medium
  - Target: Full type coverage with mypy validation
  - Current: ~50% coverage estimate

- [ ] **Add docstrings to public functions**
  - Status: ⏸️ **MINIMAL** - Some critical functions documented
  - Priority: Medium
  - Target: Google-style docstrings for all public APIs
  - Current: ~30% coverage estimate

- [ ] **Set up pre-commit hooks**
  - Status: ⏸️ **NOT IMPLEMENTED**
  - Priority: Low
  - Tools needed:
    - Black for formatting
    - Flake8 for linting
    - MyPy for type checking
  - **Note**: Manual code review currently sufficient for solo development

---

## Performance

- [ ] **Profile app performance**
  - Status: ⏸️ **NOT STARTED**
  - Priority: Low (app performs well on test devices)
  - Areas to investigate if needed:
    - Database query optimization (currently fast enough)
    - UI rendering lag (none observed)
    - Memory usage (lightweight, no issues)

- [ ] **Optimize APK size**
  - Status: ⏸️ **NOT PRIORITY**
  - Current size: ~20-25 MB (reasonable for Kivy app with KivyMD)
  - Future optimizations if needed:
    - Remove unused dependencies
    - Compress assets
    - Use ProGuard/R8 (requires buildozer config)

---

## Documentation

- [x] **✅ Update README with post-setup instructions**
  - Status: ✅ **COMPLETED** (December 27, 2025)
  - Includes: How to run desktop app, build APK, development workflow
  - Concise, feature-focused content

- [ ] **Add user guide**
  - Status: ⏸️ **DEFERRED** - Google Play Store listing will serve as initial user guide
  - Priority: Low (app is intuitive, minimal guidance needed)
  - Future: Screenshots in Play Store listing + in-app help if feedback requests it

---

## Future Enhancements (Post-MVP)

- [ ] Dark theme support (Material Design 3 dark mode)
- [ ] Habit templates (quick-start with common habits)
- [ ] Reminders/notifications (Android AlarmManager)
- [x] **✅ Backup/restore to file** (Implemented: CSV export + JSON import in v0.2.0)
- [ ] Habit notes/journal entries (per-completion notes)
- [ ] Habit categories/tags (organize by life area)
- [ ] Custom week start day (currently fixed Monday)
- [ ] Achievement badges (milestone celebrations)
- [ ] View/restore archived habits (separate screen or toggle filter)
- [x] **✅ Localization (i18n)** - Basic implementation complete (English/Spanish)

---

## Localization Technical Debt

### Current Implementation (v0.2.0)
- ✅ **Status**: Basic JSON-based translation system implemented
- ✅ **Languages**: English and Spanish
- ✅ **Features**:
  - Simple JSON translation files (`app/config/strings/en.json`, `es.json`)
  - LocalizationManager singleton for loading translations
  - Shorthand `_()` function for getting translated strings
  - String formatting support (e.g., `_("key", count=5)`)
  - Language preference persists across app restarts in database

### Future Migration Plan
- **Target**: Industry-standard `gettext` with .po/.mo files
- **Reason**: Better tooling, pluralization rules, context-aware translations, translator-friendly
- **Priority**: Medium (after Phase 3 or when adding 3rd language)
- **Tools**: babel, polib, or standard gettext utilities
- **Benefits**:
  - Professional translation workflow
  - Better IDE/editor support for translators
  - Pluralization (e.g., "1 habit" vs "2 habits")
  - Context comments for translators
  - Industry-standard format (.po files)

### Translation Coverage Status (v0.2.0)
- ✅ Account screen (settings, data management)
- ✅ Bottom navigation tabs
- ✅ App toolbar title
- ✅ Habit form (labels, buttons, validation messages)
- ✅ Main screen (habits list, section headers)
- ⏸️ Analytics screen (view switcher, labels) - **Partially implemented**
- ⏸️ Dialogs and error messages - **Partially implemented**

**Note**: Core user-facing strings are translated, full coverage needs completion for Analytics screen.

---

## Resolved Technical Debt (v0.2.0)

### Build Issues ✅ **RESOLVED in v0.1.3**
- ✅ Missing KivyMD dependencies (filetype, pillow) - Added to requirements
- ✅ Python 3.10+ type hint syntax (`T | None`) - Changed to `Optional[T]`
- ✅ Window.size on Android causing crashes - Platform-specific config added

### Database Schema ✅ **RESOLVED in v0.1.0**
- ✅ Foreign key CASCADE delete - Implemented and tested
- ✅ Unique name constraint (case-insensitive) - Using COLLATE NOCASE
- ✅ Composite indexes for performance - Added idx_completions_habit_date

### UI/UX Issues ✅ **RESOLVED in v0.1.4-v0.2.0**
- ✅ FAB blocking habit cards - Fixed with FloatLayout and bottom scroll padding
- ✅ Section headers too large - Reduced by 20% (H6 → Subtitle1)
- ✅ Heatmap not updating after completions - Added smart cache invalidation
- ✅ Month view misalignment - Fixed weekday column alignment for all habits

---

**Summary for v0.2.0 Release:**
- ✅ **Phase 1 (MVP)**: 100% complete
- ✅ **Phase 2 (Core Features)**: ~90% complete (missing only Week Navigation PRD 2.2.3)
- ⏸️ **Phase 3 (Analytics)**: ~70% complete (heatmap done, visual export deferred)
- ⚠️ **Critical Gap**: NO AUTOMATED TESTS - must be addressed before production
- ✅ **Google Play Ready**: AAB build configured, compliance verified (API 35, NDK 26b, 64-bit)

**Next Priorities:**
1. Internal testing on Google Play (v0.2.0)
2. Implement automated test suite (unit + integration tests)
3. Complete Phase 2: Week Navigation (PRD 2.2.3)
4. Complete Phase 3: Progress Statistics (PRD 2.2.5)
5. Address localization coverage gaps (Analytics screen)
