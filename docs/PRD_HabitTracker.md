# Product Requirements Document (PRD)
# Personal Habit Tracker - Android App

**Version:** 1.0  
**Date:** December 8, 2024  
**Author:** Davs  
**Status:** Draft

---

## 1. Product Overview

### 1.1 Purpose
A personal, offline-first Android habit tracking application designed for individual use without dependency on cloud services or paid subscriptions. The app enables users to track daily, weekly, and monthly habits with visual analytics and progress monitoring.

### 1.2 Target User
- Single user (personal use)
- Android device owner
- Needs simple, reliable habit tracking
- Values privacy and offline functionality
- Frustrated with limited free tiers of existing apps

### 1.3 Key Principles
- **Offline-First**: No internet connection required
- **Privacy**: All data stored locally on device
- **Simplicity**: Clean, intuitive interface
- **Flexibility**: Support multiple tracking frequencies
- **Free**: No paywalls or subscription limits

---

## 2. Feature Specification

### 2.1 VITAL FEATURES (MVP - Phase 1)

#### 2.1.1 Habit Management
**Resource:** `models/database.py`, `logic/habit_manager.py`, `views/habit_form.py`

**Database Operations:**
- Create new habit with name, color, goal_type, goal_count
- Read all habits from database
- Update existing habit properties
- Delete habit and associated completion records
- Archive/unarchive habits (soft delete)

**Business Logic:**
- Validate habit name (non-empty, max 50 characters)
- Validate goal count (positive integer, max 100)
- Validate color (hex format: #RRGGBB)
- Ensure unique habit names per user
- Calculate current period for habit (today for daily, current week for weekly, current month for monthly)

**View Requirements:**
- Form with text input for habit name
- Color picker with predefined palette (8-12 colors)
- Dropdown for goal type: Daily, Weekly, Monthly
- Number spinner for goal count (1-100)
- Save and Cancel buttons
- Validation error messages

#### 2.1.2 Completion Tracking
**Resource:** `models/database.py`, `logic/habit_manager.py`, `views/habit_card.py`

**Database Operations:**
- Insert completion record (habit_id, date, count)
- Update completion count for existing date
- Query completions for specific habit and date
- Query completions for date range (week/month)

**Business Logic:**
- Increment completion count for current date
- Decrement completion count (minimum 0)
- Calculate progress: current_count / goal_count
- Determine if goal met (current_count >= goal_count)
- Get completion status for each day in current period

**View Requirements:**
- Display current count and goal (e.g., "3 / 5 times")
- Increment button (+ icon)
- Visual indicator when goal is met (checkmark or highlight)
- Immediate UI update on increment
- Prevent negative counts

#### 2.1.3 Habit List Display
**Resource:** `views/main_screen.py`, `views/habit_card.py`

**View Structure:**
- Grouped sections: "Weekly Goals" and "Monthly Goals"
- Each section contains relevant habits based on goal_type
- Empty state message when no habits in section
- Floating Action Button (FAB) to add new habit

**Habit Card Layout:**
- Colored label/badge with habit name
- Current progress display (X / Y format)
- Increment button on right side
- Tap card to edit habit (future: phase 2)

**View Logic:**
- Load habits from database on screen load
- Group habits by goal_type
- Sort habits by creation date (newest first)
- Refresh list when habit added/edited/deleted
- Refresh counts when completion incremented

#### 2.1.4 Data Persistence
**Resource:** `models/database.py`

**Database Schema:**

```sql
CREATE TABLE habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    color TEXT NOT NULL,
    goal_type TEXT NOT NULL CHECK(goal_type IN ('daily', 'weekly', 'monthly')),
    goal_count INTEGER NOT NULL CHECK(goal_count > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived INTEGER DEFAULT 0
);

CREATE TABLE completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date DATE NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    UNIQUE(habit_id, date)
);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

**Database Operations:**
- Initialize database on first app launch
- Create tables if not exist
- Handle foreign key constraints
- Implement migrations for schema updates (future)

**File Storage:**
- Database file: `habit_tracker.db`
- Location: App's internal storage (private directory)
- No external storage permissions required

---

### 2.2 INTERESTING FEATURES (Phase 2)

#### 2.2.1 Streak Tracking
**Resource:** `logic/analytics.py`, `logic/habit_manager.py`

**Business Logic:**
- Calculate consecutive days/weeks/months of goal completion
- Break streak when goal not met in period
- Reset streak counter to 0
- Track best streak (all-time high)

**Calculation Rules:**
- Daily habits: Check consecutive days
- Weekly habits: Check consecutive weeks (Mon-Sun)
- Monthly habits: Check consecutive months
- Period is "complete" when goal_count reached
- Current period not counted in streak until complete

**View Requirements:**
- Flame icon with streak number
- Display on habit card
- Show only when streak > 0
- Different visual treatment for active vs broken streak

#### 2.2.2 Calendar Heatmap Visualization
**Resource:** `views/reports_screen.py`, `components/heatmap.py`, `logic/analytics.py`

**Data Structure:**
- Generate map of date -> completion_percentage
- Group by habit
- Support month, week, year views

**Calculation:**
- Completion percentage = (completions / goal_count) * 100
- Cap at 100%
- Handle partial completions (e.g., 3/5 = 60%)

**Visualization:**
- Grid layout: 7 columns (week) or 31 cells (month)
- Color intensity based on completion percentage:
  - 0%: Light gray or background color
  - 1-49%: Light shade of habit color
  - 50-99%: Medium shade of habit color
  - 100%: Full habit color
- Include date labels
- Show current date indicator

**View Requirements:**
- Tabs for Week/Month/Year views
- Date navigation: Previous/Next arrows, Today button
- Display multiple habits in scrollable list
- Each habit shows: name, percentage, heatmap grid
- Export buttons: Save Image, Share Report

#### 2.2.3 Week Navigation
**Resource:** `views/main_screen.py`, `logic/date_utils.py`

**View Components:**
- Horizontal strip showing 7 days
- Format: Day name abbreviation + date number (Mon 8, Tue 9)
- Current day highlighted with border/background
- Tap to select different day

**Logic:**
- Calculate week start (Monday) and end (Sunday)
- Generate 7 date objects for current week
- Handle week transitions (previous/next week buttons optional)
- Update habit completions based on selected date

**Behavior:**
- Default to current day on app launch
- Selecting different day updates all habit counts
- Visual indicator for selected day
- Show completions for selected date only

#### 2.2.4 Collapsible Sections
**Resource:** `components/collapsible.py`, `views/main_screen.py`

**Component Structure:**
- Header with icon, title, and count badge
- Dropdown arrow indicating state
- Content container for child widgets
- Smooth expand/collapse animation

**Logic:**
- Toggle state on header tap
- Save state in app memory (not persisted)
- Count badge shows number of habits in section
- Default state: expanded

**View Requirements:**
- Section title with icon (calendar/grid icon)
- Right-aligned dropdown arrow
- Badge with habit count
- Animate content height on toggle
- Rotate arrow icon 180° when expanded

#### 2.2.5 Progress Statistics
**Resource:** `logic/analytics.py`, `views/reports_screen.py`

**Metrics to Calculate:**
- Completion percentage for current period
- Total completions count
- Days/weeks/months active
- Current streak
- Best streak

**Display:**
- Show percentage on reports screen
- Format: "X%" next to habit name in heatmap view
- Color-code percentage (red < 50%, yellow 50-79%, green >= 80%)

---

### 2.3 OPTIONAL FEATURES (Phase 3)

#### 2.3.1 Yearly Goals
**Resource:** `models/database.py`, `logic/habit_manager.py`

**Implementation:**
- Add 'yearly' to goal_type enum
- Calculate current year boundaries
- Display in separate "Yearly Goals" section
- Heatmap shows 12 months grid

#### 2.3.2 Export/Share Reports
**Resource:** `views/reports_screen.py`, `utils/export.py`

**Export Options:**
- Save heatmap as PNG image to gallery
- Share image via Android share intent
- Export CSV data (future)

**Implementation:**
- Render heatmap to image buffer
- Save to device storage with timestamp filename
- Use Android share API for sharing

#### 2.3.3 Negative Habit Tracking
**Resource:** `models/database.py`, `logic/habit_manager.py`

**Concept:**
- Track habits to avoid/reduce (e.g., "Skip junk food")
- Goal is to stay UNDER count (inverse logic)
- Visual indicator (red when exceeded, green when under)

**Implementation:**
- Add goal_behavior field: 'positive' or 'negative'
- Reverse progress calculation for negative habits
- Different icon/color scheme

#### 2.3.4 Timer Integration
**Resource:** `views/timer_screen.py`, `logic/timer_manager.py`

**Features:**
- Start timer for time-based habits
- Track duration instead of count
- Background timer support
- Notification when complete

#### 2.3.5 Bottom Navigation Tabs
**Resource:** `views/main_screen.py`

**Tabs:**
- Habits (main list view)
- Reports (analytics/heatmap)
- Calendar (alternative view)
- Statistics (aggregated data)
- Settings

---

## 3. Technical Specifications

### 3.1 Technology Stack

**Language:** Python 3.9+

**Framework:**
- Kivy 2.2.1+ (UI framework)
- KivyMD 1.1.1+ (Material Design components)

**Database:**
- SQLite3 (built-in Python library)

**Visualization:**
- Kivy graphics primitives for heatmap
- Matplotlib (optional, if more complex charts needed)

**Build Tool:**
- Buildozer 1.5.0+ (Android APK compilation)

**Dependencies:**
```
kivy>=2.2.1
kivymd>=1.1.1
python-dateutil>=2.8.2
```

### 3.2 Project Structure

```
habit_tracker/
│
├── main.py                          # App entry point
│
├── models/
│   ├── __init__.py
│   ├── database.py                  # SQLite operations
│   └── schemas.py                   # Data models
│
├── logic/
│   ├── __init__.py
│   ├── habit_manager.py             # Habit business logic
│   ├── analytics.py                 # Statistics calculations
│   └── date_utils.py                # Date utilities
│
├── views/
│   ├── __init__.py
│   ├── main_screen.py               # Main habit list
│   ├── habit_form.py                # Add/edit form
│   └── reports_screen.py            # Analytics screen
│
├── components/
│   ├── __init__.py
│   ├── habit_card.py                # Habit list item
│   ├── collapsible.py               # Expandable section
│   ├── color_picker.py              # Color selector
│   └── heatmap.py                   # Calendar heatmap
│
├── assets/
│   └── icons/                       # Icon files
│
├── config/
│   ├── __init__.py
│   └── constants.py                 # App constants
│
├── utils/
│   ├── __init__.py
│   └── helpers.py                   # Utility functions
│
├── buildozer.spec                   # Build configuration
├── requirements.txt                 # Dependencies
└── README.md                        # Documentation
```

### 3.3 Data Models

#### Habit Model
```python
class Habit:
    id: int
    name: str
    color: str  # hex format: #RRGGBB
    goal_type: str  # 'daily', 'weekly', 'monthly'
    goal_count: int
    created_at: datetime
    archived: bool
```

#### Completion Model
```python
class Completion:
    id: int
    habit_id: int
    date: date
    count: int
    completed_at: datetime
```

### 3.4 Key Algorithms

#### Streak Calculation
```
1. Get all completions for habit, sorted by date
2. Group completions by period (day/week/month based on goal_type)
3. Check each period: did completions >= goal_count?
4. Count consecutive "success" periods working backwards from today
5. Stop when encountering "failure" period or run out of data
6. Return count of consecutive successes
```

#### Period Boundaries
```
Daily: 
  - Start: today at 00:00:00
  - End: today at 23:59:59

Weekly (Monday start):
  - Start: Monday of current week at 00:00:00
  - End: Sunday of current week at 23:59:59

Monthly:
  - Start: 1st of current month at 00:00:00
  - End: Last day of current month at 23:59:59
```

#### Progress Calculation
```
progress_percentage = (current_count / goal_count) * 100
goal_met = current_count >= goal_count
remaining = max(0, goal_count - current_count)
```

### 3.5 UI/UX Guidelines

**Color Palette (Default Habit Colors):**
- Red: #E57373
- Orange: #FFB74D
- Yellow: #FFF176
- Green: #81C784
- Teal: #4DB6AC
- Blue: #64B5F6
- Purple: #BA68C8
- Pink: #F06292

**Typography:**
- Primary font: Roboto
- Habit name: 16sp, Medium weight
- Progress text: 14sp, Regular
- Section headers: 18sp, Medium

**Spacing:**
- Card padding: 16dp
- Section spacing: 24dp
- Element spacing: 8dp

**Interactions:**
- Button press: Ripple effect
- Card tap: Navigate to edit (Phase 2)
- Swipe: Delete habit (Phase 3)

### 3.6 Performance Requirements

- Database queries: < 50ms for main screen load
- UI updates: < 16ms (60 FPS)
- App launch time: < 2 seconds
- Database size: Support 1000+ completions without lag

### 3.7 Platform Requirements

**Minimum Android Version:** Android 7.0 (API Level 24)  
**Target Android Version:** Android 13 (API Level 33)  
**Screen Sizes:** Support phones (4.5" - 7")  
**Orientation:** Portrait only (locked)

### 3.8 Permissions Required

- None (all data stored in app's private directory)

---

## 4. Development Phases

### Phase 1: MVP (Week 1)
**Goal:** Basic functional habit tracker

**Deliverables:**
- [ ] Project structure setup
- [ ] Database schema implementation
- [ ] Add/edit habit form
- [ ] Main screen with habit list
- [ ] Increment completion functionality
- [ ] Basic progress display
- [ ] Local data persistence

**Success Criteria:**
- User can create habits
- User can log completions
- Data persists across app restarts
- App builds and runs on Android device

---

### Phase 2: Core Features (Week 2)
**Goal:** Enhanced usability and motivation features

**Deliverables:**
- [ ] Weekly/Monthly habit grouping
- [ ] Collapsible sections
- [ ] Streak calculation and display
- [ ] Week day navigation
- [ ] Improved UI with KivyMD components
- [ ] Edit/delete habit functionality

**Success Criteria:**
- Habits organized by frequency
- Users see streak motivation
- UI matches reference screenshots
- Full CRUD operations work

---

### Phase 3: Analytics (Week 3)
**Goal:** Visual progress tracking and insights

**Deliverables:**
- [ ] Reports screen with tabs
- [ ] Calendar heatmap visualization
- [ ] Date range navigation
- [ ] Completion percentage calculations
- [ ] Export heatmap as image

**Success Criteria:**
- Users see visual progress patterns
- Heatmap renders correctly for all periods
- Export functionality works

---

### Phase 4: Polish & Deployment (Week 4)
**Goal:** Production-ready application

**Deliverables:**
- [ ] UI refinements and animations
- [ ] Edge case handling
- [ ] Error messaging
- [ ] Performance optimization
- [ ] APK build and testing
- [ ] User documentation

**Success Criteria:**
- No critical bugs
- Smooth animations
- App tested on physical device
- APK installable and functional

---

## 5. Quality Assurance

### 5.1 Test Cases

#### Habit Management
- [ ] Create habit with all required fields
- [ ] Create habit with empty name (should fail)
- [ ] Create habit with duplicate name
- [ ] Edit habit and verify changes persist
- [ ] Delete habit and verify completions removed
- [ ] Create 50+ habits (stress test)

#### Completion Tracking
- [ ] Increment completion and verify count updates
- [ ] Increment multiple times in same day
- [ ] Verify completion resets for new day/week/month
- [ ] Complete goal and verify visual indicator
- [ ] Test with goal_count = 1 and goal_count = 100

#### Streak Calculation
- [ ] Complete habit for 7 consecutive days, verify streak = 7
- [ ] Miss one day, verify streak resets to 0
- [ ] Complete weekly habit for 4 weeks, verify streak = 4
- [ ] Test edge case: complete on last day of period

#### Data Persistence
- [ ] Create habits, close app, reopen and verify data
- [ ] Log completions, close app, reopen and verify counts
- [ ] Clear app data, verify database reinitializes

#### UI/UX
- [ ] Verify all buttons respond to touch
- [ ] Test on different screen sizes (if possible)
- [ ] Verify scroll works with many habits
- [ ] Test rapid button tapping (debounce)

### 5.2 Error Handling

**Database Errors:**
- Catch SQLite exceptions and log errors
- Show user-friendly error message: "Unable to save data"
- Graceful degradation: app continues to function

**Input Validation:**
- Display inline error messages on form
- Disable save button until form valid
- Clear error messages on input change

**Edge Cases:**
- No habits: Show empty state with "Add Habit" prompt
- No completions: Show 0 / X for all habits
- Date edge cases: Handle leap years, month boundaries

---

## 6. Future Enhancements (Post-Launch)

### 6.1 Potential Features
- [ ] Habit templates (pre-made habits to choose from)
- [ ] Reminders/notifications
- [ ] Backup/restore to file
- [ ] Dark theme
- [ ] Habit notes/journal entries
- [ ] Habit categories/tags
- [ ] Custom week start day (Monday vs Sunday)
- [ ] Multiple completions per day visualization
- [ ] Progress charts (line/bar graphs)
- [ ] Achievement badges

### 6.2 Technical Improvements
- [ ] Database migrations system
- [ ] Unit tests for business logic
- [ ] CI/CD pipeline
- [ ] Localization (i18n)
- [ ] Accessibility improvements
- [ ] Performance profiling

---

## 7. Constraints & Assumptions

### 7.1 Constraints
- Single user only (no multi-user support)
- No cloud sync (purely local)
- No web version
- Limited to Android platform
- No in-app purchases or monetization

### 7.2 Assumptions
- User has Android 7.0+ device
- User comfortable with English language
- User understands basic habit tracking concepts
- Device has sufficient storage (< 100MB)

---

## 8. Success Metrics

Since this is a personal app, success is qualitative:

- **Functionality:** All vital features work without crashes
- **Usability:** Can track habits daily without friction
- **Reliability:** Data never lost, app stable
- **Performance:** No noticeable lag in normal usage
- **Personal Value:** Actually used daily for 30+ days

---

## 9. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Kivy learning curve | Delays Phase 1 | Medium | Review Kivy docs, start with simple UI |
| Buildozer compilation issues | Cannot test on device | Medium | Test early, use Docker for build environment |
| Database corruption | Data loss | Low | Implement backup, test edge cases |
| Performance on older devices | Poor UX | Low | Test on minimum API level device |
| Scope creep | Never finish MVP | Medium | Strict phase adherence, resist feature additions |

---

## 10. Sign-off

**Developer:** Davs  
**Start Date:** December 8, 2024  
**Target Completion:** January 5, 2025 (4 weeks)

---

## Appendix A: Reference Screenshots

See uploaded images:
- Image 1: Main screen with weekly/monthly goals
- Image 2: Reports screen with heatmap visualization
- Image 3: New habit creation form

---

## Appendix B: Glossary

- **Completion:** A single instance of performing a habit
- **Goal:** The target number of completions for a period
- **Period:** The timeframe for a goal (day/week/month)
- **Streak:** Consecutive periods where goal was met
- **Heatmap:** Calendar visualization showing completion patterns
- **MVP:** Minimum Viable Product - essential features only
- **FAB:** Floating Action Button
- **APK:** Android Package - installable app file

---

**Document End**
