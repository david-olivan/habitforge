# HabitForge

[![Release](https://github.com/david-olivan/habitforge/actions/workflows/release.yml/badge.svg)](https://github.com/david-olivan/habitforge/actions/workflows/release.yml)
[![Android Build Compliance](https://github.com/david-olivan/habitforge/actions/workflows/android-compliance.yml/badge.svg)](https://github.com/david-olivan/habitforge/actions/workflows/android-compliance.yml)

<p align="center">
  <img src="app/assets/icons/habitforge-logo.svg" alt="HabitForge Logo" width="400">
</p>

<p align="center">
  <strong>Forge Your Habits, One Day at a Time</strong>
</p>

A privacy-focused, offline-first habit tracking application for Android built with Python and Kivy.

## About

HabitForge is a personal habit tracker designed to work completely offline with no artificial limits, subscriptions, or cloud requirements. All data is stored locally on your device using SQLite.

Track daily, weekly, and monthly habits with visual analytics including streak tracking and GitHub-style calendar heatmaps showing your progress patterns over time.

Built as a learning project to leverage Python expertise for Android development, avoiding the need to learn new languages while still delivering a native-feeling Material Design 3 experience.

## Features

### Habit Management
- Create, edit, and delete habits with custom names and colors
- Set daily, weekly, or monthly goals with configurable target counts (1-100)
- 8-color Material Design palette for habit organization
- Archive habits to hide them without losing historical data

### Tracking & Progress
- Quick increment buttons to log habit completions
- Real-time progress display (current count / goal)
- Visual indicators when goals are met
- 5-day date navigation to view and update past progress
- Grouped habit lists by goal type (Daily/Weekly/Monthly)
- Collapsible sections with habit counts

### Analytics & Visualization
- **Streak Tracking:** Consecutive periods meeting your goal, displayed with flame icons
- **Calendar Heatmaps:** GitHub-style grids showing completion patterns with color intensity
- **Multiple Views:** Week, Month, and Year heatmap perspectives
- **Date Navigation:** Browse historical data with Previous/Next/Today buttons
- **Per-Habit Analytics:** Each habit uses its assigned color in heatmap visualizations

### Data Management
- **Localization:** Full English/Spanish language support
- **Export:** Save all habit data to CSV format
- **Import:** Load habit data from JSON files
- **Delete:** Permanently remove all data with confirmation

## Tech Stack

- **Language:** Python 3.11
- **UI Framework:** Kivy 2.3.1 + KivyMD 1.2.0 (Material Design 3)
- **Database:** SQLite3 (local storage)
- **Build Tool:** Buildozer 1.5.0
- **Target Platform:** Android 7.0+ (API 24), Target API 35
- **Architecture:** ARM64 (arm64-v8a)

## Quick Start

### Development Setup

```bash
# Clone repository
git clone https://github.com/david-olivan/habitforge.git
cd habitforge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run on desktop
cd app
python main.py
```

### Building APK

**Using Docker (Recommended):**

```bash
# Build debug APK using provided scripts
./scripts/build-apk.sh

# Build release APK
./scripts/build-release.sh

# APK output: bin/habitforge-{version}-arm64-v8a-{debug|release}.apk
```

**Using Buildozer directly:**

```bash
# First build (downloads SDK/NDK, takes 30-60 minutes)
buildozer android debug

# Subsequent builds (2-5 minutes)
buildozer android debug

# Build and install on connected device
buildozer android debug deploy run
```

## Project Structure

```
habitforge/
├── app/
│   ├── main.py                    # Entry point (KivyMD app)
│   ├── models/                    # Database & schemas
│   │   ├── database.py           # SQLite CRUD operations
│   │   ├── schemas.py            # Pydantic models
│   │   └── schema.sql            # Database schema reference
│   ├── views/                     # UI screens
│   │   ├── main_container.py     # Bottom navigation
│   │   ├── main_screen.py        # Habits list
│   │   ├── analytics_content.py  # Heatmap visualization
│   │   ├── account_content.py    # Settings/data management
│   │   ├── habit_form.py         # Create/edit habit
│   │   └── ...
│   ├── components/                # Reusable UI widgets
│   │   ├── habit_card.py         # Habit display card
│   │   ├── heatmap_grid.py       # Calendar heatmap
│   │   ├── date_strip.py         # Date navigation
│   │   └── ...
│   ├── logic/                     # Business logic
│   │   ├── habit_manager.py      # Habit validation
│   │   ├── completion_manager.py # Progress tracking
│   │   ├── streak_calculator.py  # Streak calculation
│   │   ├── heatmap_data.py       # Heatmap data generation
│   │   └── ...
│   ├── config/                    # Configuration
│   │   ├── constants.py          # Color palette, limits
│   │   └── strings/              # i18n translations
│   └── assets/                    # Icons, images
├── buildozer.spec                 # Android build config
├── requirements.txt               # Desktop dependencies
├── requirements-app.txt           # Android APK dependencies
└── scripts/                       # Build utilities
```

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

**Version:** 0.2.0
**Last Updated:** December 28, 2025
