# HabitForge - Personal Android App

A privacy-focused, offline-first habit tracking application for Android, built with Python and Kivy.

<p align="center">
  <img src="assets/icons/habitforge-logo.svg" alt="HabitForge Logo" width="400">
</p>

<p align="center">
  <strong>Forge Your Habits, One Day at a Time</strong>
</p>

---

## Table of Contents

1. [Project Context](#project-context)
2. [Project Overview](#project-overview)
3. [Quick Start](#quick-start)
4. [Development Environment Setup](#development-environment-setup)
5. [Building the APK](#building-the-apk)
6. [Development Workflow](#development-workflow)
7. [Project Structure](#project-structure)
8. [Testing on Device](#testing-on-device)
9. [Troubleshooting](#troubleshooting)
10. [Resources](#resources)

---

## Project Context

### Background

This project originated from frustration with existing Android habit tracking apps that either:
- Require paid subscriptions for basic features
- Limit free users to 5 or fewer habits
- Require internet connectivity and cloud accounts
- Include unnecessary social features

**Goal:** Create a simple, personal habit tracker that:
- Works completely offline
- Has no artificial limits on habits
- Stores all data locally on the device
- Provides clean visualizations and analytics
- Is free and privacy-respecting

### Technology Choice

After evaluating several cross-platform options (React Native, Flutter, PWA), **Python with Kivy** was selected because:
- Leverage existing Python expertise (no new language to learn)
- Native SQLite integration for local storage
- KivyMD provides Material Design components
- Buildozer simplifies Android APK compilation
- Fastest path to a working prototype

### Design Reference

The app design is inspired by existing habit trackers, with reference screenshots showing:
- Main screen with grouped weekly/monthly habits
- Calendar heatmap visualization for progress tracking
- Clean, card-based UI with color-coded habits
- Increment buttons for easy habit logging

---

## Project Overview

### Key Features

**Phase 1 (MVP):**
- Create/edit/delete habits with custom names and colors
- Track daily, weekly, and monthly habits
- Increment completion counts
- Local SQLite database storage
- Basic list view

**Phase 2 (Enhancement):**
- Streak tracking with flame icons
- Calendar heatmap visualizations
- Week navigation (day selector)
- Collapsible sections for habit grouping
- Completion percentage statistics

**Phase 3 (Polish):**
- Export reports as images
- Additional time periods (yearly goals)
- UI animations and refinements

### Tech Stack

- **Language:** Python 3.9+
- **UI Framework:** Kivy 2.2.1+, KivyMD 1.1.1+
- **Database:** SQLite3
- **Build Tool:** Buildozer 1.5.0+
- **Target Platform:** Android 7.0+ (API Level 24)

---

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Linux (Ubuntu 20.04+ recommended) or WSL2 on Windows
- Git
- At least 4GB RAM available
- 10GB free disk space

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd habit_tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run on desktop (for development)
python main.py
```

---

## Development Environment Setup

### Option 1: Linux (Recommended)

```bash
# Update system packages
sudo apt update
sudo apt upgrade

# Install system dependencies
sudo apt install -y \
    python3-pip \
    python3-venv \
    build-essential \
    git \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev

# Install Java (required for Buildozer)
sudo apt install -y openjdk-11-jdk

# Set JAVA_HOME
echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' >> ~/.bashrc
source ~/.bashrc

# Install Python dependencies
pip install --upgrade pip
pip install buildozer cython==0.29.33
pip install -r requirements.txt
```

### Option 2: WSL2 on Windows

1. Enable WSL2 in Windows
2. Install Ubuntu 20.04 or 22.04 from Microsoft Store
3. Follow the Linux setup instructions above

### Option 3: Docker (Isolated Environment)

```bash
# Pull Buildozer Docker image
docker pull kivy/buildozer

# Run buildozer in container
docker run -it --rm \
    -v "$(pwd)":/app \
    kivy/buildozer \
    buildozer android debug
```

### Verify Installation

```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check Java version
java -version  # Should be OpenJDK 11

# Check Buildozer installation
buildozer --version
```

---

## Building the APK

### Initial Setup

1. **Initialize Buildozer configuration:**

```bash
buildozer init
```

This creates `buildozer.spec` file. Key settings to configure:

```ini
[app]
title = Habit Tracker
package.name = habittracker
package.domain = com.davs

# Version information
version = 0.1

# Source files
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Requirements
requirements = python3,kivy,kivymd,sqlite3

# Android specific
android.permissions = 
android.api = 31
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True

# Orientation
orientation = portrait

# Icon (optional, add later)
# icon.filename = %(source.dir)s/assets/icon.png
```

2. **First Build (takes 30-60 minutes):**

```bash
buildozer android debug
```

This will:
- Download Android SDK/NDK (~2GB)
- Download Python-for-Android
- Compile dependencies
- Build APK

The APK will be in: `bin/habittracker-0.1-arm64-v8a-debug.apk`

### Subsequent Builds

After the first build, subsequent builds are much faster (2-5 minutes):

```bash
# Clean build (if needed)
buildozer android clean

# Build debug APK
buildozer android debug

# Build and deploy to connected device
buildozer android debug deploy run

# View logcat output
buildozer android logcat
```

### Build Optimization

**Quick Development Builds:**
```bash
# Skip unnecessary steps
buildozer android debug --skip-sdk-update
```

**Clean Build (when dependencies change):**
```bash
buildozer android clean
buildozer android debug
```

**Build for specific architecture:**
```bash
# ARM 64-bit (most modern devices)
buildozer android debug --arch=arm64-v8a

# ARM 32-bit (older devices)
buildozer android debug --arch=armeabi-v7a
```

### Release Build (for distribution)

```bash
# Generate keystore (one time)
keytool -genkey -v -keystore my-release-key.keystore \
    -alias habittracker -keyalg RSA -keysize 2048 -validity 10000

# Build signed release APK
buildozer android release

# Sign the APK
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
    -keystore my-release-key.keystore \
    bin/habittracker-0.1-arm64-v8a-release-unsigned.apk habittracker

# Verify signature
jarsigner -verify -verbose -certs \
    bin/habittracker-0.1-arm64-v8a-release-unsigned.apk
```

---

## Testing on Device

### Method 1: ADB Install (Recommended)

```bash
# Enable USB debugging on Android device:
# Settings > About Phone > Tap "Build Number" 7 times
# Settings > Developer Options > Enable USB Debugging

# Connect device via USB
adb devices  # Should list your device

# Install APK
adb install -r bin/habittracker-0.1-arm64-v8a-debug.apk

# View logs
adb logcat | grep python
```

### Method 2: File Transfer

1. Copy APK from `bin/` folder to device
2. Open file manager on device
3. Tap APK file
4. Enable "Install from Unknown Sources" if prompted
5. Install app

### Method 3: Buildozer Deploy

```bash
# Build and install in one command
buildozer android debug deploy run

# View logs
buildozer android logcat
```

### Testing Checklist

After installing on device:

- [ ] App launches without crashes
- [ ] Can create new habit
- [ ] Can increment completion count
- [ ] Data persists after closing app
- [ ] UI renders correctly on device screen
- [ ] Touch interactions work smoothly
- [ ] No performance issues (lag/freeze)

---

## Development Workflow

### Daily Development Cycle

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Make code changes

# 3. Test on desktop first (faster iteration)
python main.py

# 4. Build and test on device when ready
buildozer android debug deploy run

# 5. View logs if issues occur
buildozer android logcat | grep python
```

### Recommended Development Process

#### Phase 1: Desktop Development

Develop and test most features on desktop first:

```bash
# Run app on desktop
python main.py

# Hot reload with Kivy's DevTools (optional)
pip install kivy-devtools
kivy-devtools run main.py
```

Benefits:
- Faster iteration (no build time)
- Easier debugging (Python debugger works)
- Immediate error messages

#### Phase 2: Device Testing

Test on Android device periodically:

```bash
# After completing a feature
buildozer android debug deploy run
```

Focus device testing on:
- Touch interactions
- Screen size/resolution
- Performance (lag, memory)
- Android-specific features (notifications, etc.)

### Git Workflow

```bash
# Feature branch workflow
git checkout -b feature/streak-tracking

# Make changes, commit frequently
git add .
git commit -m "feat: implement streak calculation logic"

# When feature complete, merge to main
git checkout main
git merge feature/streak-tracking

# Tag releases
git tag -a v0.1.0 -m "MVP Release"
git push origin v0.1.0
```

### Code Organization Best Practices

1. **Separation of Concerns:**
   - `models/`: Data structures and database operations only
   - `logic/`: Business logic, no UI code
   - `views/`: UI components, minimal logic
   - `components/`: Reusable UI widgets

2. **Database Access:**
   - Always use context managers for database connections
   - Centralize queries in `models/database.py`
   - Never perform queries in view code

3. **Error Handling:**
   - Wrap database operations in try/except
   - Log errors for debugging
   - Show user-friendly messages in UI

4. **Testing Strategy:**
   - Write unit tests for `logic/` modules
   - Test database operations manually
   - UI testing on actual device

### Debugging Tools

#### Desktop Debugging

```python
# Add print statements
print(f"Habit count: {len(habits)}")

# Use Python debugger
import pdb; pdb.set_trace()

# Kivy logging
from kivy.logger import Logger
Logger.info('HabitTracker: User incremented habit')
```

#### Android Debugging

```bash
# View all logs
adb logcat

# Filter Python logs
adb logcat | grep python

# Filter app logs
adb logcat | grep habittracker

# Clear log buffer
adb logcat -c

# Save logs to file
adb logcat -d > logcat.txt
```

#### Common Issues and Solutions

**App crashes on launch:**
```bash
# Check logcat for errors
adb logcat | grep -i error

# Common causes:
# - Missing dependency in requirements
# - Database initialization error
# - KivyMD version mismatch
```

**UI not updating:**
```python
# Force UI refresh in Kivy
from kivy.clock import Clock
Clock.schedule_once(lambda dt: self.refresh_ui(), 0)
```

**Database locked error:**
```python
# Always close connections
with Database() as db:
    # operations here
    pass
# Connection automatically closed
```

---

## Project Structure

```
habit_tracker/
│
├── main.py                      # Entry point: HabitTrackerApp class
│   ├── Initializes Kivy app
│   ├── Loads main screen
│   └── Handles app lifecycle
│
├── models/                      # Data layer
│   ├── database.py             # SQLite operations
│   │   ├── create_tables()
│   │   ├── CRUD operations
│   │   └── Query methods
│   └── schemas.py              # Data classes (Habit, Completion)
│
├── logic/                       # Business logic
│   ├── habit_manager.py        # Core habit operations
│   │   ├── create_habit()
│   │   ├── get_progress()
│   │   └── calculate_period_boundaries()
│   ├── analytics.py            # Statistics and calculations
│   │   ├── calculate_streak()
│   │   ├── get_completion_percentage()
│   │   └── generate_heatmap_data()
│   └── date_utils.py           # Date manipulation
│       ├── get_week_boundaries()
│       ├── get_month_boundaries()
│       └── format_date()
│
├── views/                       # UI screens
│   ├── main_screen.py          # Main habit list view
│   │   ├── Load habits
│   │   ├── Display grouped sections
│   │   └── Handle user interactions
│   ├── habit_form.py           # Add/edit habit screen
│   │   ├── Form inputs
│   │   ├── Validation
│   │   └── Save to database
│   └── reports_screen.py       # Analytics/heatmap view
│       ├── Tab navigation
│       ├── Heatmap rendering
│       └── Export functionality
│
├── components/                  # Reusable UI widgets
│   ├── habit_card.py           # Individual habit list item
│   │   ├── Display habit info
│   │   ├── Increment button
│   │   └── Progress indicator
│   ├── collapsible.py          # Expandable section
│   │   ├── Header with count
│   │   ├── Toggle state
│   │   └── Animated content
│   ├── color_picker.py         # Color selection widget
│   │   ├── Color grid
│   │   └── Selection handling
│   └── heatmap.py              # Calendar heatmap widget
│       ├── Grid layout
│       ├── Color intensity mapping
│       └── Date labels
│
├── assets/                      # Static resources
│   ├── icons/                  # App icons
│   └── fonts/                  # Custom fonts (if needed)
│
├── config/                      # Configuration
│   ├── constants.py            # App-wide constants
│   │   ├── Color palette
│   │   ├── Default settings
│   │   └── Database config
│
├── utils/                       # Utilities
│   └── helpers.py              # General helper functions
│
├── tests/                       # Unit tests (future)
│   ├── test_habit_manager.py
│   ├── test_analytics.py
│   └── test_database.py
│
├── buildozer.spec              # Android build configuration
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore patterns
└── README.md                   # This file
```

### File Responsibilities

**main.py:**
- Initialize Kivy application
- Set up window size (for desktop testing)
- Load KivyMD theme
- Navigate to main screen

**models/database.py:**
- Database connection management
- Table creation and migrations
- CRUD operations for habits and completions
- Query builders for analytics

**logic/habit_manager.py:**
- Business rules for habits
- Validation logic
- Period calculations (week/month boundaries)
- Progress tracking logic

**views/main_screen.py:**
- Screen layout with KivyMD components
- Habit list rendering
- Event handlers (button clicks)
- Navigation to other screens

**components/habit_card.py:**
- Single habit display widget
- Increment button logic
- Visual updates on completion

---

## Troubleshooting

### Build Issues

#### Problem: Buildozer fails with "Command failed"

**Solution:**
```bash
# Clean build directory
buildozer android clean

# Update buildozer
pip install --upgrade buildozer

# Try again
buildozer android debug
```

#### Problem: "SDK not found" or "NDK not found"

**Solution:**
```bash
# Remove .buildozer directory
rm -rf .buildozer

# Rebuild (will re-download SDK/NDK)
buildozer android debug
```

#### Problem: "No space left on device"

**Solution:**
```bash
# Clean old build artifacts
buildozer android clean
rm -rf .buildozer/android/platform/build-*

# Check disk space
df -h
```

#### Problem: Java version issues

**Solution:**
```bash
# Install correct Java version
sudo apt install openjdk-11-jdk

# Set JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' >> ~/.bashrc
```

### Runtime Issues

#### Problem: App crashes immediately on launch

**Check logcat:**
```bash
adb logcat | grep -i error
```

**Common causes:**
- Missing Python module in requirements
- Database file permissions
- KivyMD version conflict

**Solution:**
```bash
# Add missing module to buildozer.spec
requirements = python3,kivy,kivymd,sqlite3,<missing-module>

# Rebuild
buildozer android clean
buildozer android debug
```

#### Problem: Database errors on device

**Solution:**
```python
# In models/database.py, ensure proper path
import os
from kivy.app import App

def get_db_path():
    if App.get_running_app():
        # On Android
        return os.path.join(App.get_running_app().user_data_dir, 'habit_tracker.db')
    else:
        # On desktop
        return 'habit_tracker.db'
```

#### Problem: UI elements not visible

**Check:**
- KivyMD version compatibility
- Screen size definitions
- Color contrast (text on background)

**Debug:**
```python
# In views, add debug prints
from kivy.logger import Logger
Logger.info(f'Screen size: {Window.size}')
Logger.info(f'Number of habits: {len(self.habits)}')
```

### Performance Issues

#### Problem: App feels slow/laggy

**Optimize:**
```python
# Reduce database queries
# Cache habits list in memory
self.habits_cache = []

# Update UI with Clock.schedule
from kivy.clock import Clock
Clock.schedule_once(lambda dt: self.update_ui(), 0.1)

# Avoid rebuilding entire UI
# Update specific widgets instead
```

#### Problem: Heatmap rendering slow

**Solution:**
```python
# Render heatmap in background thread (future enhancement)
# Or simplify visualization
# Or limit displayed date range
```

---

## Resources

### Official Documentation

- **Kivy:** https://kivy.org/doc/stable/
- **KivyMD:** https://kivymd.readthedocs.io/
- **Buildozer:** https://buildozer.readthedocs.io/
- **Python-for-Android:** https://python-for-android.readthedocs.io/

### Tutorials

- Kivy Crash Course: https://www.youtube.com/watch?v=F7UKmK9eQLY
- KivyMD Tutorial: https://www.youtube.com/playlist?list=PLdNh20AHwM7tJ7Y5XQqKb5z3ZPd9P6Pqj
- Buildozer Guide: https://kivy.org/doc/stable/guide/packaging-android.html

### Community

- Kivy Discord: https://chat.kivy.org/
- Stack Overflow: Tag `kivy` or `kivy-language`
- Reddit: r/kivy

### Similar Projects

- Kivy Examples: https://github.com/kivy/kivy/tree/master/examples
- KivyMD Kitchen Sink: https://github.com/kivymd/KivyMD

### Development Tools

- **Android Studio:** For advanced Android debugging
- **Genymotion:** Android emulator (alternative to physical device)
- **Scrcpy:** Mirror Android screen to desktop for testing

---

## Development Timeline

### Week 1: MVP
- Day 1-2: Setup project structure, database
- Day 3-4: Implement habit CRUD operations
- Day 5-6: Build main screen UI
- Day 7: First APK build and device testing

### Week 2: Enhancement
- Day 8-9: Implement streak tracking
- Day 10-11: Build reports screen
- Day 12-13: Create heatmap visualization
- Day 14: Testing and bug fixes

### Week 3: Polish
- Day 15-16: UI refinements and animations
- Day 17-18: Add export functionality
- Day 19-20: Performance optimization
- Day 21: Final testing

### Week 4: Documentation & Release
- Day 22-23: Write user documentation
- Day 24-25: Create demo video/screenshots
- Day 26-27: Build release APK
- Day 28: Final deployment and celebration! 🎉

---

## Contributing

This is a personal project, but if you want to fork and modify:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## License

This project is personal and educational. No license specified.

---

## Contact

**Developer:** Davs  
**Email:** [Your email if you want to share]  
**GitHub:** [Your GitHub profile]

---

## Acknowledgments

- Kivy team for the amazing framework
- KivyMD contributors for Material Design components
- Habit tracking app developers for UI inspiration
- Python community for excellent documentation

---

## Version History

- **v0.1.0** (TBD) - MVP Release
  - Basic habit creation and tracking
  - Local SQLite storage
  - Simple list view
  
- **v0.2.0** (TBD) - Enhancement Release
  - Streak tracking
  - Calendar heatmap
  - Reports screen
  
- **v0.3.0** (TBD) - Polish Release
  - Export functionality
  - Animations
  - Performance improvements

---

**Happy Habit Tracking! 📈**

Last Updated: December 8, 2024
