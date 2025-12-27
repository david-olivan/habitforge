# Technical Debt & Future Tasks

This file tracks technical debt, deferred tasks, and future improvements for HabitForge.

---

## Build & Deployment

### Android Build Testing
- [ ] **Test first Docker-based APK build**
  - Status: Not tested yet
  - Priority: High
  - Notes: First build takes 30-60 min (downloads SDK/NDK ~2GB), subsequent builds 5-10 min
  - Command: `bash scripts/build_android.sh` or `.\scripts\build_android.ps1`
  - Expected output: `bin/habitforge-0.1.0-arm64-v8a-debug.apk`

- [ ] **Install and test APK on physical Android device**
  - Status: Deferred (no device available during setup)
  - Priority: High
  - Method 1: `adb install -r bin/habitforge-0.1.0-arm64-v8a-debug.apk`
  - Method 2: File transfer and manual install
  - Test: Verify "Hello World - HabitForge" appears on device

### App Icon
- [ ] **Convert SVG icons to PNG format**
  - Status: Not done
  - Priority: Medium
  - Current: SVG files in `app/assets/icons/`
  - Needed: PNG format (512x512 recommended) for Android
  - Update `buildozer.spec`: Uncomment and set `icon.filename`

### Release Build
- [ ] **Configure signing for release APK**
  - Status: Not configured
  - Priority: Low (only needed for Play Store)
  - Requires: Generate keystore
  - Command: `keytool -genkey -v -keystore my-release-key.keystore ...`

---

## Phase 1: MVP Implementation

### Database Layer
- [ ] **Implement `models/database.py`**
  - SQLite connection management
  - Table creation (habits, completions, settings)
  - CRUD operations
  - Context manager for connections

- [ ] **Implement `models/schemas.py`**
  - Habit data class
  - Completion data class
  - Type hints and validation

### Business Logic
- [ ] **Implement `logic/habit_manager.py`**
  - Habit CRUD operations
  - Validation logic
  - Period boundary calculations (week/month)
  - Progress tracking

- [ ] **Implement `logic/date_utils.py`**
  - Get week boundaries (Monday-Sunday)
  - Get month boundaries
  - Date formatting helpers

### Configuration
- [ ] **Implement `config/constants.py`**
  - Color palette (8 colors from PRD)
  - App-wide constants
  - Default settings

### UI Layer
- [ ] **Enhance `app/main.py`**
  - Load KivyMD theme
  - Initialize database
  - Set up navigation
  - Replace "Hello World" with real UI

- [ ] **Implement `views/main_screen.py`**
  - Habit list display
  - Grouped sections (Weekly/Monthly)
  - Floating Action Button (FAB) for add habit
  - Refresh on data change

- [ ] **Implement `views/habit_form.py`**
  - Text input for habit name
  - Color picker
  - Goal type dropdown (Daily/Weekly/Monthly)
  - Goal count spinner
  - Save/Cancel buttons

- [ ] **Implement `components/habit_card.py`**
  - Habit display widget
  - Color indicator
  - Progress display (X / Y format)
  - Increment button
  - Visual feedback on goal completion

---

## Phase 2: Core Features

- [x] **Implement streak calculation**
  - Consecutive period completion tracking
  - Visual indicator (flame icon)

- [ ] **Implement collapsible sections**
  - Expandable/collapsible habit groups
  - Smooth animations
  - **Future enhancement**: Persist collapsed state in settings table across app sessions

- [ ] **Implement week navigation**
  - Day selector strip (Mon-Sun)
  - Current day highlight

- [ ] **Add edit/delete functionality**
  - Long-press or swipe to delete
  - Tap card to edit

---

## Phase 3: Analytics

- [ ] **Implement reports screen**
  - Tab navigation (Week/Month/Year)
  - Date range selector

- [ ] **Implement calendar heatmap**
  - Color intensity based on completion %
  - Interactive grid layout

- [ ] **Add export functionality**
  - Save heatmap as PNG
  - Share via Android intent

---

## Testing

- [ ] **Write unit tests**
  - Test habit_manager logic
  - Test analytics calculations
  - Test date utilities

- [ ] **Manual testing checklist**
  - Create habit
  - Increment completion
  - Data persists across restarts
  - UI renders on different screen sizes

---

## Code Quality

- [ ] **Add type hints throughout codebase**
  - Currently: No type hints
  - Target: Full type coverage

- [ ] **Add docstrings to public functions**
  - Currently: Minimal documentation
  - Target: Google-style docstrings

- [ ] **Set up pre-commit hooks**
  - Black for formatting
  - Flake8 for linting
  - MyPy for type checking

---

## Performance

- [ ] **Profile app performance**
  - Identify bottlenecks
  - Optimize database queries
  - Reduce UI lag

- [ ] **Optimize APK size**
  - Remove unused dependencies
  - Compress assets
  - Use ProGuard (if needed)

---

## Documentation

- [ ] **Update README with post-setup instructions**
  - How to run desktop app
  - How to build APK
  - Development workflow

- [ ] **Add user guide**
  - How to use the app
  - Feature explanations
  - Screenshots

---

## Future Enhancements (Post-MVP)

- [ ] Dark theme support
- [ ] Habit templates
- [ ] Reminders/notifications
- [x] Backup/restore to file (Implemented: Export/Import CSV backups)
- [ ] Habit notes/journal entries
- [ ] Habit categories/tags
- [ ] Custom week start day
- [ ] Achievement badges
- [x] Localization (i18n) - **Basic implementation complete, see below for improvement plan**

---

## Localization Technical Debt

### Current Implementation (December 21, 2025)
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
- **Priority**: Medium (after Phase 2 completion)
- **Tools**: babel, polib, or standard gettext utilities
- **Benefits**:
  - Professional translation workflow
  - Better IDE/editor support for translators
  - Pluralization (e.g., "1 habit" vs "2 habits")
  - Context comments for translators
  - Industry-standard format (.po files)

### Translation Coverage
- ✅ Account screen (settings, data management)
- ✅ Bottom navigation tabs
- ✅ App toolbar title
- ⏸️ Main screen (habits list, section headers) - Partially implemented
- ⏸️ Habit form (labels, buttons, validation messages) - Not yet implemented
- ⏸️ Analytics screen (view switcher, labels) - Not yet implemented
- ⏸️ Dialogs and error messages - Partially implemented

**Note**: Core strings are translated, but full coverage of all UI elements needs completion.

---

**Last Updated:** December 21, 2025
**Next Review:** After Phase 2 completion