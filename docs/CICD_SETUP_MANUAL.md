# CI/CD Setup Manual - Habit Tracker
## Progressive Implementation Guide

**Target:** Automate releases with changelog generation and APK building  
**Strategy:** Manual tagging with automated changelog, versioning, and APK builds  
**Device:** Honor Magic6 (ARM64-v8a architecture)

---

## Table of Contents

1. [Stage 1: Basics - Changelog Generation](#stage-1-basics---changelog-generation-week-1)
2. [Stage 2: Local Build + Auto Release](#stage-2-local-build--auto-release-week-2)
3. [Stage 3: Docker Build Integration](#stage-3-docker-build-integration-week-3)
4. [Stage 4: Polish & Optimization](#stage-4-polish--optimization-week-4)
5. [Conventional Commits for Claude Code](#conventional-commits-for-claude-code)
6. [Testing & Troubleshooting](#testing--troubleshooting)

---

## Stage 1: Basics - Changelog Generation (Week 1)

**Goal:** Set up automatic changelog generation when you push tags, no APK building yet.

**Time Investment:** 1-2 hours  
**Complexity:** Low  
**Deliverables:** Working changelog automation

### Step 1.1: Create GitHub Repository

If you haven't already:

```bash
# Initialize git (if needed)
cd habit_tracker
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Buildozer
.buildozer/
bin/
*.apk

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Local testing
habit_tracker.db
test_*.py
EOF

# Initial commit
git add .
git commit -m "chore: initial project setup"

# Create GitHub repo (via GitHub CLI or web interface)
gh repo create habit-tracker --public --source=. --remote=origin
git push -u origin main
```

### Step 1.2: Create Changelog Configuration

Create the file `.github/changelog-config.json`:

```bash
mkdir -p .github
```

**File content explanation:**

This file tells the changelog generator:
- **categories:** How to group commits (Features, Bug Fixes, etc.)
- **ignore_labels:** Which commits to skip (work-in-progress, testing commits)
- **label_extractor:** Regex pattern to parse conventional commit messages
- **template:** How to format the output

The generator will:
1. Read all commits between the last tag and current tag
2. Parse each commit message using regex
3. Extract the type (feat, fix, docs, etc.)
4. Group commits by type into categories
5. Generate formatted markdown output

**Key patterns:**
- `feat(scope): message` → Goes to "🚀 Features" section
- `fix(scope): message` → Goes to "🐛 Bug Fixes" section
- `docs(scope): message` → Goes to "📚 Documentation" section
- Commits with `wip` in message → Ignored

### Step 1.3: Create Basic Workflow

Create the file `.github/workflows/release.yml`:

**This workflow does:**

1. **Trigger:** Runs only when you push a tag matching `v*.*.*` pattern
   - Example: `v0.1.0`, `v1.2.3`, `v0.2.0-beta`
   - Does NOT run on regular commits

2. **Checkout:** Gets your code with full git history
   - `fetch-depth: 0` means "fetch all commits" (needed for changelog)
   - Without this, only the latest commit is fetched

3. **Generate Changelog:** 
   - Reads commits between last tag and current tag
   - Parses using the config file you created
   - Outputs markdown-formatted changelog

4. **Create Release:**
   - Creates a GitHub Release associated with your tag
   - Uses generated changelog as release notes
   - Marks 0.x.x versions as "pre-release"
   - Marks 1.x.x+ as stable release

**Important note:** This workflow creates a release but doesn't build an APK yet. You'll add that in Stage 3.

### Step 1.4: Test the Workflow

**Step-by-step testing process:**

1. **Make some test commits:**

```bash
# Commit 1: A feature
git add .
git commit -m "feat(database): add habits table schema

Created SQLite table for storing habit data with fields:
- id, name, color, goal_type, goal_count"

# Commit 2: Another feature
git commit -m "feat(ui): create main screen layout" --allow-empty

# Commit 3: A bug fix
git commit -m "fix(database): handle null values in habit name" --allow-empty

# Commit 4: Documentation
git commit -m "docs(readme): add installation instructions" --allow-empty

# Commit 5: WIP (will be ignored)
git commit -m "wip: testing UI colors" --allow-empty

# Push commits
git push origin main
```

**Expected result:** Nothing happens yet - the workflow only runs on tags, not commits.

2. **Create and push your first test tag:**

```bash
# Create annotated tag
git tag -a v0.0.1-test -m "Test release for CI/CD setup"

# Push the tag
git push origin v0.0.1-test
```

**Expected result:** 
- GitHub Actions workflow starts automatically
- Check: Go to your GitHub repo → Actions tab
- You'll see a workflow run named "Release Build" or similar
- Click on it to watch it run in real-time

3. **Monitor the workflow:**

Watch each step:
- ✅ Checkout code (should take ~5 seconds)
- ✅ Generate Changelog (should take ~10 seconds)
- ✅ Create Release (should take ~5 seconds)

**If it succeeds:**
- Go to your GitHub repo → Releases tab
- You'll see a new release titled `v0.0.1-test`
- The release notes will contain your changelog with sections:
  - 🚀 Features (2 items)
  - 🐛 Bug Fixes (1 item)
  - 📚 Documentation (1 item)
  - No "wip" commit (it was ignored)

4. **Review the generated changelog:**

It should look something like:

```markdown
## 🚀 Features
- feat(database): add habits table schema
- feat(ui): create main screen layout

## 🐛 Bug Fixes
- fix(database): handle null values in habit name

## 📚 Documentation
- docs(readme): add installation instructions
```

**Analysis:**
- Clean, categorized output
- Professional formatting
- Easy to read for users
- Useful for tracking what changed

5. **Clean up test release:**

```bash
# Delete local tag
git tag -d v0.0.1-test

# Delete remote tag
git push origin :refs/tags/v0.0.1-test

# Delete release on GitHub
# Go to Releases → Click the test release → Delete
```

### Step 1.5: Understanding What Just Happened

**The magic behind the scenes:**

1. **You pushed a tag** → GitHub detected it
2. **Workflow triggered** → GitHub Actions runner (Ubuntu VM) started
3. **Changelog generated** → Tool parsed your commit messages
4. **Release created** → Visible on GitHub with nice formatting

**Why this is valuable:**
- No more manually writing release notes
- Consistent formatting every time
- Encourages good commit message discipline
- Takes 30 seconds instead of 30 minutes

### Stage 1 Checkpoint

✅ **What you should have now:**
- `.github/changelog-config.json` file
- `.github/workflows/release.yml` file
- Successfully created and deleted a test release
- Understanding of how changelog generation works

✅ **What you can do:**
- Push tags to automatically generate changelogs
- See formatted release notes on GitHub
- Track what changed between versions

❌ **What you CAN'T do yet:**
- Automatically build APK files
- Version bumping in buildozer.spec
- Download APK from GitHub releases

**Next:** Stage 2 will add automatic versioning and manual APK attachment.

---

## Stage 2: Local Build + Auto Release (Week 2)

**Goal:** Automatically update version number and create release draft. You build APK locally and attach it.

**Time Investment:** 2-3 hours  
**Complexity:** Medium  
**Deliverables:** Auto-versioning + release draft workflow

### Step 2.1: Add Version Bumping

**Update your workflow file** (`.github/workflows/release.yml`):

Add a new step after "Generate Changelog" and before "Create Release":

**What this step does:**

1. **Extracts version from tag:**
   - `${GITHUB_REF#refs/tags/v}` removes `refs/tags/v` prefix
   - Example: `refs/tags/v0.1.0` → `0.1.0`

2. **Updates buildozer.spec:**
   - Uses `sed` to find line starting with `version = `
   - Replaces entire line with new version
   - Example: `version = 0.0.0` → `version = 0.1.0`

3. **Displays result:**
   - Echoes the new version for verification
   - Useful for debugging if something goes wrong

**Why use sed?**
- Simple, no external dependencies
- Works on any Linux runner
- One-line solution
- Reliable for simple replacements

### Step 2.2: Make Release a Draft

**Update the "Create Release" step:**

Change `draft: false` to `draft: true`

**Why create drafts?**
- Gives you time to review the changelog
- Lets you build and attach APK before publishing
- You can edit release notes if needed
- Prevents premature announcements

**Workflow:**
1. Push tag → Workflow runs → Draft release created
2. You build APK locally: `buildozer android debug`
3. You go to GitHub → Releases → Edit draft
4. You attach APK file
5. You click "Publish release"

### Step 2.3: Configure Pre-release Tagging

**Update the "Create Release" step again:**

**What this does:**

- Checks if version starts with `0.` (e.g., `0.1.0`, `0.2.3`)
- If yes: Marks as "pre-release" (yellow tag on GitHub)
- If no: Marks as full release (green tag on GitHub)

**Why this matters:**
- Signals to users that 0.x versions are not stable
- GitHub shows "Latest release" badge only for non-pre-releases
- When you hit 1.0.0, it automatically becomes a full release

### Step 2.4: Test Version Bumping

1. **Update your buildozer.spec:**

Make sure it has a version line:
```ini
[app]
version = 0.0.0
```

2. **Commit and push:**

```bash
git add buildozer.spec
git commit -m "chore(build): initialize version in buildozer.spec"
git push origin main
```

3. **Create a real version tag:**

```bash
git tag -a v0.1.0 -m "MVP Release - Basic habit tracking"
git push origin v0.1.0
```

4. **Check the workflow:**

- Go to Actions tab
- Watch the workflow run
- Click on "Update Version" step
- You should see output like:
  ```
  Updated version to: 0.1.0
  version = 0.1.0
  ```

5. **Check the release:**

- Go to Releases tab
- You'll see a DRAFT release titled `v0.1.0`
- It will have a yellow "Pre-release" badge
- Changelog will be formatted nicely

6. **Build and attach APK:**

```bash
# Build locally
buildozer android debug

# APK will be at: bin/habittracker-0.1.0-arm64-v8a-debug.apk
```

On GitHub:
- Click "Edit" on the draft release
- Drag and drop the APK file
- Optionally edit the release notes
- Click "Publish release"

### Step 2.5: Verify Everything Works

**Checklist:**
- [ ] Tag pushed successfully
- [ ] Workflow ran without errors
- [ ] Draft release created
- [ ] Release marked as "Pre-release"
- [ ] Changelog generated correctly
- [ ] APK built locally
- [ ] APK attached to release
- [ ] Release published successfully

**Test downloading:**
- Go to the published release
- Click the APK file to download
- Install on your Honor Magic6
- Verify it works

### Stage 2 Checkpoint

✅ **What you have now:**
- Automatic version bumping in buildozer.spec
- Draft releases for review before publishing
- Pre-release tagging for 0.x versions
- Complete release workflow (with manual APK)

✅ **What you can do:**
- Push tags to create draft releases
- Review changelog before publishing
- Attach locally-built APK
- Publish when ready

✅ **Benefits gained:**
- 90% automation (only APK build is manual)
- Professional-looking releases
- Version consistency guaranteed
- Much faster than fully manual process

❌ **Still missing:**
- Automatic APK building in CI
- One-command release process

**Next:** Stage 3 will add Docker-based APK building.

---

## Stage 3: Docker Build Integration (Week 3)

**Goal:** Fully automate APK building using Docker in GitHub Actions.

**Time Investment:** 4-6 hours (mostly waiting for builds)  
**Complexity:** High  
**Deliverables:** Complete end-to-end automation

### Step 3.1: Understanding Docker Build Strategy

**Why Docker?**
- Pre-configured environment with all Android tools
- Consistent builds (same result locally and in CI)
- No need to install Android SDK/NDK on runner
- Maintained by Kivy team

**How it works:**
1. GitHub Actions runner pulls Docker image
2. Your code is mounted into container
3. Buildozer runs inside container
4. APK is copied out to runner
5. APK is uploaded to release

**Image:** `kivy/buildozer:latest` (or specific version like `1.5.0`)

**Trade-offs:**
- ✅ Cleaner, more maintainable
- ✅ Faster setup (no SDK installation)
- ✅ Reproducible builds
- ❌ First build still takes 30-45 minutes (downloads dependencies)
- ❌ Subsequent builds: 5-10 minutes (with caching)

### Step 3.2: Prepare Your Project

**Create buildozer.spec if you haven't:**

```bash
buildozer init
```

**Edit buildozer.spec for your Honor Magic6:**

Key settings to verify/update:

```ini
[app]
title = Habit Tracker
package.name = habittracker
package.domain = com.davs
version = 0.1.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Requirements - adjust based on your needs
requirements = python3,kivy==2.2.1,kivymd==1.1.1

# Android specific
android.permissions = 
android.api = 31
android.minapi = 24
android.ndk = 25b
android.sdk = 31
android.accept_sdk_license = True

# Architecture - Honor Magic6 uses ARM64
android.archs = arm64-v8a

# Orientation
orientation = portrait

# Optional: Add icon later
# icon.filename = %(source.dir)s/assets/icon.png
```

**Important notes:**
- `android.archs = arm64-v8a` - This is crucial for Honor Magic6
- Building only one architecture makes builds faster
- If you want to support more devices later, use `arm64-v8a,armeabi-v7a`

### Step 3.3: Add Docker Build Step to Workflow

**Update `.github/workflows/release.yml`:**

Add this step after "Update Version" and before "Create Release":

**Explanation of each part:**

**Docker command breakdown:**
- `docker run` - Start a container
- `--rm` - Remove container when done
- `-v "$(pwd)":/app` - Mount current directory to /app in container
- `-w /app` - Set working directory to /app
- `kivy/buildozer` - Use official Kivy Docker image
- `buildozer android debug` - Command to run inside container

**Permission fix:**
- Docker runs as root, creates files owned by root
- `sudo chown -R` changes ownership to current user
- Needed so GitHub Actions can access the APK

**Find APK:**
- Searches `bin/` directory for `.apk` files
- Saves path to GitHub Actions variable
- Used later to upload to release

### Step 3.4: Update Release Step to Include APK

**Update the "Create Release" step:**

**What changed:**
- Added `files:` parameter
- Uses the APK path from previous step
- Automatically uploads APK as release asset

**Result:**
- Release will have APK attached automatically
- No more manual upload needed
- APK is named properly with version and architecture

### Step 3.5: Add Caching for Faster Builds

**Add this step BEFORE the Docker build step:**

**What this caches:**
- `.buildozer/` directory (Android SDK, NDK, build artifacts)
- Cache key includes `buildozer.spec` content hash
- If buildozer.spec changes, cache is invalidated

**Performance impact:**
- First build: 30-45 minutes (downloads everything)
- Second build: 5-10 minutes (uses cache)
- Cache size: ~3-5 GB
- Cache stored for 7 days if not used

**When cache is invalidated:**
- You change buildozer.spec (dependencies, versions, etc.)
- 7 days pass without using it
- You manually clear cache on GitHub

### Step 3.6: Test the Full Workflow

**Important:** This first build will take a long time. Start it when you can leave it running.

1. **Commit all changes:**

```bash
git add .
git commit -m "ci(release): add Docker-based APK building

- Use kivy/buildozer Docker image
- Add build caching for faster subsequent builds
- Automatically attach APK to releases"
git push origin main
```

2. **Create a test tag:**

```bash
git tag -a v0.1.1-test -m "Test Docker build workflow"
git push origin v0.1.1-test
```

3. **Monitor the build:**

Go to Actions tab and watch:
- ✅ Checkout (5 seconds)
- ✅ Restore cache (10 seconds, will miss on first run)
- ✅ Generate Changelog (10 seconds)
- ✅ Update Version (5 seconds)
- ⏳ Build APK with Docker (30-45 minutes on first run)
- ✅ Find APK (5 seconds)
- ✅ Create Release (10 seconds)

**What to watch for:**
- Docker image pull (first time: ~2 minutes)
- Buildozer downloading Android SDK/NDK (~10 minutes)
- Buildozer downloading Python dependencies (~5 minutes)
- Actual compilation (~15-20 minutes)
- If anything fails, check the logs carefully

4. **If build succeeds:**

- Check Releases tab
- You'll see v0.1.1-test release
- APK should be attached automatically
- Download and test on your Honor Magic6

5. **If build fails:**

Common issues and solutions:

**Error: "No space left on device"**
```yaml
# Add before build step:
- name: Free Disk Space
  run: |
    sudo rm -rf /usr/share/dotnet
    sudo rm -rf /opt/ghc
    sudo rm -rf /usr/local/share/boost
    df -h
```

**Error: "Buildozer command not found"**
- The Docker image includes buildozer, but verify image name
- Try specific version: `kivy/buildozer:1.5.0`

**Error: "Permission denied"**
- Add sudo to chown command (already in example above)
- Check file permissions in repo

**Error: "APK not found"**
- Check if build actually completed
- Verify APK_PATH variable was set
- Look in bin/ directory manually

6. **Test a second build (with cache):**

```bash
# Make a small change
git commit -m "docs: update readme" --allow-empty
git push origin main

# Tag again
git tag -a v0.1.2-test -m "Test cached build"
git push origin v0.1.2-test
```

This time:
- Cache restore should hit (~1 minute)
- Build should take only 5-10 minutes
- Much faster!

### Step 3.7: Clean Up Test Releases

```bash
# Delete test tags locally
git tag -d v0.1.1-test v0.1.2-test

# Delete test tags remotely
git push origin :refs/tags/v0.1.1-test
git push origin :refs/tags/v0.1.2-test

# Delete releases on GitHub UI
# Releases → Each test release → Delete
```

### Stage 3 Checkpoint

✅ **What you have now:**
- Fully automated APK building in CI
- Docker-based reproducible builds
- Build caching for speed
- Complete end-to-end automation
- One command to release: `git tag && git push`

✅ **What you can do:**
- Push tag → APK built automatically
- Download APK directly from GitHub
- Share releases with anyone via link
- True continuous deployment!

✅ **Workflow now:**
```bash
# Week of development with many commits
git commit -m "feat(ui): add color picker"
git commit -m "feat(db): implement streak tracking"
git commit -m "fix(ui): button alignment"
# ... many more commits

# Release time
git tag v0.2.0
git push origin v0.2.0

# Wait 5-10 minutes, APK ready to download!
```

🎉 **You've achieved full CI/CD!**

---

## Stage 4: Polish & Optimization (Week 4)

**Goal:** Improve workflow reliability, speed, and user experience.

**Time Investment:** 3-4 hours  
**Complexity:** Medium  
**Deliverables:** Production-ready CI/CD pipeline

### Step 4.1: Add Build Status Badges

**Add to your README.md:**

```markdown
# Habit Tracker

[![Release](https://github.com/YOUR_USERNAME/habit-tracker/actions/workflows/release.yml/badge.svg)](https://github.com/YOUR_USERNAME/habit-tracker/actions/workflows/release.yml)
[![Latest Release](https://img.shields.io/github/v/release/YOUR_USERNAME/habit-tracker)](https://github.com/YOUR_USERNAME/habit-tracker/releases/latest)

Your project description here...
```

**Benefits:**
- Quick visual status of latest build
- Professional appearance
- Click badge to see workflow runs
- Shows latest version number

### Step 4.2: Add Multiple Architecture Support (Optional)

**If you want to support more devices:**

Edit `buildozer.spec`:
```ini
android.archs = arm64-v8a,armeabi-v7a
```

Update workflow to handle multiple APKs:

```yaml
- name: Find APKs
  id: find_apks
  run: |
    APK_FILES=$(find bin -name "*.apk" -type f)
    echo "apk_files<<EOF" >> $GITHUB_OUTPUT
    echo "$APK_FILES" >> $GITHUB_OUTPUT
    echo "EOF" >> $GITHUB_OUTPUT

- name: Create Release
  uses: softprops/action-gh-release@v1
  with:
    body: ${{ steps.changelog.outputs.changelog }}
    draft: true
    prerelease: ${{ startsWith(github.ref, 'refs/tags/v0.') }}
    files: bin/*.apk  # Upload all APKs
```

**Trade-off:**
- ✅ Supports more devices
- ❌ Build time doubles (~10-20 minutes)
- ❌ Release size doubles (~40MB → ~80MB)

For personal use on Honor Magic6, single architecture is fine.

### Step 4.3: Add Release Notes Template

**Create `.github/RELEASE_TEMPLATE.md`:**

```markdown
## What's New in {{ version }}

{{ changelog }}

## Installation

1. Download the APK below
2. Enable "Install from Unknown Sources" on your Android device
3. Install the APK
4. Open Habit Tracker and enjoy!

## Supported Devices

- Android 7.0 (API 24) or higher
- Tested on Honor Magic6
- ARM64-v8a architecture

## Checksums

{{ checksums }}

---

**Full Changelog**: https://github.com/YOUR_USERNAME/habit-tracker/compare/{{ previous_tag }}...{{ tag }}
```

**Update workflow to use template:**

This is more advanced and requires custom scripting. For simplicity, you can manually edit release notes after they're created.

### Step 4.4: Add Build Timeout Protection

**Update workflow:**

```yaml
jobs:
  release:
    runs-on: ubuntu-latest
    timeout-minutes: 90  # Fail if build takes over 90 min
```

**Why:**
- Prevents runaway builds from consuming all your Actions minutes
- Normal build: 5-45 minutes
- Timeout at 90 minutes is safe
- Gets notified if something goes wrong

### Step 4.5: Add Failure Notifications

**Add this step at the end of your workflow:**

```yaml
- name: Notify on Failure
  if: failure()
  run: |
    echo "Build failed! Check logs at ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
```

**For more advanced notifications:**
- Email: Use `action-send-mail`
- Discord: Use `discord-webhook-notify`
- Slack: Use `slack-notify`
- Telegram: Use `telegram-action`

Example with Discord:

```yaml
- name: Discord Notification
  if: failure()
  uses: sarisia/actions-status-discord@v1
  with:
    webhook: ${{ secrets.DISCORD_WEBHOOK }}
    status: ${{ job.status }}
    title: "Release Build Failed"
    description: "Tag ${{ github.ref_name }} failed to build"
```

### Step 4.6: Optimize Cache Strategy

**Current caching is basic. Improve it:**

```yaml
- name: Cache Buildozer
  uses: actions/cache@v3
  with:
    path: |
      .buildozer
      ~/.buildozer
    key: buildozer-${{ runner.os }}-${{ hashFiles('buildozer.spec') }}-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      buildozer-${{ runner.os }}-${{ hashFiles('buildozer.spec') }}-
      buildozer-${{ runner.os }}-
```

**Improvements:**
- Multiple restore keys (fallback if exact match not found)
- Includes requirements.txt in hash
- Caches user buildozer directory too

### Step 4.7: Add Manual Trigger Option

**Update workflow trigger:**

```yaml
on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:  # Manual trigger
    inputs:
      version:
        description: 'Version to build (e.g., 0.1.0)'
        required: true
        type: string
```

**Benefits:**
- Can manually trigger builds from GitHub UI
- Useful for testing without creating tags
- Actions tab → Select workflow → Run workflow button

### Step 4.8: Create a Release Checklist

**Add to your project docs:**

```markdown
## Release Checklist

Before tagging a release:

- [ ] All tests pass locally
- [ ] buildozer.spec version is a placeholder (will be auto-updated)
- [ ] CHANGELOG manually reviewed for accuracy
- [ ] README updated with new features
- [ ] APK tested on Honor Magic6
- [ ] No known critical bugs
- [ ] Git status is clean (no uncommitted changes)

Release process:

1. Ensure main branch is up to date: `git pull origin main`
2. Create annotated tag: `git tag -a vX.Y.Z -m "Release message"`
3. Push tag: `git push origin vX.Y.Z`
4. Monitor Actions tab for build progress
5. When complete, review draft release
6. Edit release notes if needed
7. Publish release
8. Download APK and verify on device
9. Share release link if needed
```

### Stage 4 Checkpoint

✅ **What you have now:**
- Production-ready CI/CD pipeline
- Status badges for quick visual feedback
- Optimized caching for fast builds
- Failure protection and notifications
- Manual trigger option for testing
- Professional release process

✅ **Complete automation:**
```bash
git tag v0.2.0 && git push origin v0.2.0
# 10 minutes later: APK ready on GitHub
```

✅ **What the pipeline does:**
1. Detects tag push
2. Generates changelog from commits
3. Updates version in buildozer.spec
4. Builds APK in Docker container
5. Uploads APK to GitHub Release
6. Marks as pre-release if 0.x.x
7. Notifies you if anything fails

🎉 **You have a professional-grade CI/CD pipeline!**

---

## Conventional Commits for Claude Code

**Problem:** Claude Code writes commits, but you want them to follow conventional commit format.

**Solution:** Two approaches:

### Approach 1: Configuration File (Recommended)

Create `.clauderc` or `.claude/config.json` in your project root:

**How this works:**
- Claude Code reads this config when making commits
- Uses the template for all commit messages
- You provide the actual message, template adds the format

**Limitations:**
- Claude Code might not support custom commit templates yet
- More of a future feature request

### Approach 2: Commit Message Agent (Current Solution)

Create a shell script: `scripts/commit.sh`

**How to use:**

```bash
# Instead of: git commit -m "added color picker"
# Use: ./scripts/commit.sh

# The script will:
# 1. Show your staged changes
# 2. Ask you questions about the commit
# 3. Generate a proper conventional commit
```

**Integration with Claude Code:**

You can instruct Claude Code:

> "When committing changes, please use the conventional commit format:
> - feat(scope): for new features
> - fix(scope): for bug fixes
> - docs(scope): for documentation
> - chore(scope): for maintenance
> 
> Example: `feat(habits): add streak calculation logic`"

**Better yet:** Create a prompt template file for Claude Code.

Create `.claude/prompts/commit.md`:

```markdown
# Commit Message Guidelines

When writing commit messages, ALWAYS use conventional commit format:

## Format
```
<type>(<scope>): <subject>

<optional body>

<optional footer>
```

## Types
- **feat**: New feature (user-visible)
- **fix**: Bug fix (user-visible)
- **docs**: Documentation only
- **style**: Formatting, missing semicolons, etc
- **refactor**: Code restructuring without changing behavior
- **perf**: Performance improvement
- **test**: Adding tests
- **chore**: Maintenance, dependencies, build config

## Scopes
- **habits**: Habit management (CRUD, calculations)
- **ui**: User interface components
- **database**: Database operations
- **analytics**: Statistics and visualizations
- **build**: Build system, dependencies
- **ci**: CI/CD pipeline

## Examples

Good:
```
feat(habits): add streak calculation logic

Implemented algorithm to track consecutive days of goal completion.
Streak resets when goal not met for a period.

Closes #15
```

Bad:
```
added some stuff
```

## Rules
1. Subject line: imperative mood ("add" not "added")
2. Subject line: max 50 characters
3. Body: wrap at 72 characters
4. Body: explain WHAT and WHY, not HOW
5. Use footer for breaking changes and issue references

## When writing commits:
- First show me the changes being committed
- Ask what type of commit this is
- Ask what scope it affects
- Generate the commit message
- Let me review before committing
```

### Approach 3: Git Commit Template

Create `.gitmessage` in your project:

```bash
# <type>(<scope>): <subject>
# 
# <body>
# 
# <footer>

# Type: feat, fix, docs, style, refactor, perf, test, chore
# Scope: habits, ui, database, analytics, build, ci
# Subject: imperative, lowercase, no period, max 50 char
# Body: explain what and why vs. how, wrap at 72 char
# Footer: reference issues, breaking changes

# Examples:
# feat(habits): add streak tracking with flame icons
# fix(database): prevent duplicate habit names
# docs(readme): add installation instructions
```

**Configure git to use it:**

```bash
git config commit.template .gitmessage
```

**Now when you run `git commit` (without -m):**
- Opens editor with the template
- Shows examples and guidelines
- You fill in the blanks

### Recommended Setup for Claude Code

**Create all three files:**

1. `.clauderc` - For future Claude Code support
2. `scripts/commit.sh` - For interactive commits
3. `.claude/prompts/commit.md` - Instructions for Claude Code
4. `.gitmessage` - Git template for manual commits

**Workflow:**

```bash
# When Claude Code asks about commits:
# "Please read .claude/prompts/commit.md and follow those guidelines"

# Claude Code will:
# 1. Read the guidelines
# 2. Analyze your changes
# 3. Suggest a properly formatted commit message
# 4. Ask for your approval
```

**Example interaction:**

```
You: "Commit these changes"

Claude Code: "I see you've added a color picker component to the UI.
Based on conventional commit guidelines, I suggest:

feat(ui): add color picker component for habit creation

Implemented color picker with 8 preset colors.
Users can now customize habit colors when creating new habits.
Component is reusable across different forms.

Does this look good? [Y/n]"

You: "Yes"

Claude Code: *commits with that message*
```

### Validation Tool (Bonus)

Create `scripts/validate-commit.sh`:

**Use as git hook:**

```bash
# Copy to .git/hooks/commit-msg
cp scripts/validate-commit.sh .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg

# Now every commit is validated automatically
git commit -m "added stuff"
# ❌ Error: Commit message doesn't follow conventional format

git commit -m "feat(ui): add color picker"
# ✅ Success
```

### Integration Summary

**For maximum compatibility:**

1. **Claude Code usage:**
   - Create `.claude/prompts/commit.md`
   - Reference it in conversations
   - Claude Code reads and follows guidelines

2. **Manual commits:**
   - Configure `.gitmessage` template
   - Git opens editor with guidelines
   - Fill in the template

3. **Validation:**
   - Add commit-msg hook
   - Rejects non-compliant messages
   - Forces conventional format

4. **CI/CD:**
   - Changelog generator parses commits
   - Proper formatting = better changelogs
   - Everything works together

---

## Testing & Troubleshooting

### Testing Strategy

**Start with Safe Tests:**

1. **Test on a separate branch:**
```bash
git checkout -b test-cicd
# Make test commits
git tag v0.0.1-test
git push origin v0.0.1-test
# If it works, merge to main
```

2. **Use test tags:**
```bash
# Pattern: vX.Y.Z-test
git tag v0.1.0-test
git tag v0.2.0-alpha
git tag v0.3.0-rc1
```

3. **Delete failed attempts:**
```bash
# Local
git tag -d v0.1.0-test

# Remote
git push origin :refs/tags/v0.1.0-test

# Delete release on GitHub UI
```

### Common Issues

#### Issue 1: Workflow doesn't trigger

**Symptoms:**
- Push tag, nothing happens
- No workflow run in Actions tab

**Solutions:**
- Check tag pattern: Must match `v*.*.*`
- Check workflow file location: Must be `.github/workflows/release.yml`
- Check workflow syntax: Use YAML validator
- Check repository settings: Actions must be enabled

**Debug:**
```bash
# Check tag format
git tag
# Should show: v0.1.0 (not 0.1.0 or version-0.1.0)

# Check if file exists
ls -la .github/workflows/release.yml

# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"
```

#### Issue 2: Changelog is empty

**Symptoms:**
- Release created but no changelog
- Or changelog says "No changes"

**Causes:**
- No commits between current and last tag
- Commits don't match conventional format
- Commit types are all ignored (chore, wip, etc.)

**Solutions:**
```bash
# Check commits since last tag
git log v0.0.0..v0.1.0 --oneline

# Verify commit message format
git log --oneline | head -5
# Should show: feat(scope): message format

# Test changelog locally
# Install: npm install -g conventional-changelog-cli
conventional-changelog -p angular
```

#### Issue 3: Docker build fails

**Symptoms:**
- Build step fails with error
- Timeout after 60 minutes
- "No space left on device"

**Solutions:**

**For space issues:**
```yaml
- name: Free Space
  run: |
    sudo rm -rf /usr/share/dotnet
    sudo rm -rf /opt/ghc
    sudo rm -rf /usr/local/share/boost
    df -h
```

**For timeout issues:**
```yaml
jobs:
  release:
    timeout-minutes: 90
```

**For Docker issues:**
```yaml
# Try specific Docker image version
docker run kivy/buildozer:1.5.0

# Or use updated image
docker run kivy/buildozer:latest
```

#### Issue 4: APK not found

**Symptoms:**
- Build succeeds but no APK attached
- Error: "APK_PATH is empty"

**Solutions:**

**Check APK location:**
```bash
# Should be in: bin/habittracker-0.1.0-arm64-v8a-debug.apk

# Debug workflow:
- name: Debug APK location
  run: |
    ls -R bin/
    find . -name "*.apk" -type f
```

**Fix path in workflow:**
```yaml
- name: Find APK
  run: |
    APK_PATH=$(find bin -name "*-debug.apk" -type f | head -1)
    echo "APK_PATH=$APK_PATH" >> $GITHUB_ENV
    echo "Found APK: $APK_PATH"
```

#### Issue 5: Permission denied errors

**Symptoms:**
- "Permission denied" when accessing APK
- "Cannot read APK file"

**Solutions:**
```yaml
- name: Fix Permissions
  run: |
    sudo chown -R $USER:$USER .buildozer
    sudo chown -R $USER:$USER bin
    ls -la bin/
```

#### Issue 6: Cache not working

**Symptoms:**
- Every build takes 30+ minutes
- Cache restore step says "Cache not found"

**Debug:**
```yaml
- name: Debug Cache
  run: |
    ls -la .buildozer/ || echo "No .buildozer directory"
    du -sh .buildozer/* || echo "Empty .buildozer"
```

**Solution:**
- First build always slow (creates cache)
- Second build should be fast
- If not, check cache key in workflow matches

#### Issue 7: Version not updating

**Symptoms:**
- Build runs but buildozer.spec version unchanged
- APK has wrong version number

**Debug:**
```yaml
- name: Debug Version Update
  run: |
    echo "Tag ref: ${{ github.ref }}"
    VERSION=${GITHUB_REF#refs/tags/v}
    echo "Extracted version: $VERSION"
    cat buildozer.spec | grep "^version"
```

**Fix:**
- Make sure buildozer.spec has `version = ` line
- Check sed command syntax
- Verify file is committed after update

### Debugging Workflow

**Add debug steps:**

```yaml
- name: Debug Environment
  run: |
    echo "Event: ${{ github.event_name }}"
    echo "Ref: ${{ github.ref }}"
    echo "Ref Name: ${{ github.ref_name }}"
    echo "Working Directory: $(pwd)"
    ls -la
    
- name: Debug After Build
  if: always()
  run: |
    echo "Build completed"
    ls -R bin/ || echo "No bin directory"
    docker images
    df -h
```

### Getting Help

**Where to look:**

1. **GitHub Actions logs:**
   - Click failed workflow run
   - Expand each step to see detailed logs
   - Look for red error messages

2. **Buildozer logs:**
   - In "Build APK" step
   - Look for "BUILD FAILED" messages
   - Check for missing dependencies

3. **Docker logs:**
   - If Docker step fails
   - Check image pull errors
   - Verify container ran successfully

**How to share issues:**

When asking for help:
1. Copy the full error message
2. Share relevant workflow YAML
3. Share buildozer.spec content
4. Mention: tag name, commit count, repository size
5. Include: GitHub Actions log link

---

## Quick Reference

### Essential Commands

```bash
# Create and push tag (triggers release)
git tag -a v0.1.0 -m "Release message"
git push origin v0.1.0

# Delete tag (if mistake)
git tag -d v0.1.0                    # local
git push origin :refs/tags/v0.1.0    # remote

# List all tags
git tag -l

# View commits since last tag
git log v0.1.0..HEAD --oneline

# Check current version
grep "^version" buildozer.spec

# Test changelog generation locally
conventional-changelog -p angular -i CHANGELOG.md -s
```

### Commit Message Cheat Sheet

```bash
# Features
git commit -m "feat(habits): add streak calculation"
git commit -m "feat(ui): implement color picker component"

# Bug fixes
git commit -m "fix(database): prevent duplicate entries"
git commit -m "fix(ui): correct button alignment issue"

# Documentation
git commit -m "docs(readme): add installation steps"
git commit -m "docs(api): document habit manager methods"

# Refactoring
git commit -m "refactor(habits): extract validation logic"
git commit -m "refactor(ui): split main screen into components"

# Performance
git commit -m "perf(database): add index on habit_id column"
git commit -m "perf(ui): lazy load habit cards"

# Tests
git commit -m "test(habits): add streak calculation tests"

# Chores (won't appear in changelog)
git commit -m "chore(deps): upgrade kivy to 2.2.1"
git commit -m "chore(build): update buildozer config"

# CI/CD
git commit -m "ci(release): add Docker caching"
git commit -m "ci(workflow): fix APK upload path"
```

### Workflow Status Check

```bash
# View recent workflow runs
gh run list --workflow=release.yml

# Watch a running workflow
gh run watch

# View logs of failed run
gh run view <run-id> --log-failed

# Re-run failed workflow
gh run rerun <run-id>
```

### Version Bumping Guide

**Current: 0.1.0**

**Bug fix:** 0.1.0 → 0.1.1
- Tag: `v0.1.1`
- Commits: Only `fix` types

**New feature:** 0.1.0 → 0.2.0
- Tag: `v0.2.0`
- Commits: At least one `feat` type

**Breaking change:** 0.2.0 → 1.0.0
- Tag: `v1.0.0`
- Commits: At least one with `BREAKING CHANGE:` footer

---

## Conclusion

### What You've Achieved

✅ **Automated Release Pipeline:**
- Tag → Changelog → Version Bump → Build → Release
- 10-minute turnaround from tag to installable APK
- Professional-quality releases

✅ **Best Practices:**
- Conventional commits for clear history
- Semantic versioning for predictable releases
- Docker builds for reproducibility
- Caching for speed

✅ **Developer Experience:**
- One command to release: `git tag && git push`
- Clear, auto-generated changelogs
- No manual file attachments
- Confidence in every release

### Next Steps

**Week 1 (Now):**
- Set up Stage 1 (changelog generation)
- Practice conventional commits
- Test with a few releases

**Week 2:**
- Add Stage 2 (auto-versioning)
- Test draft releases
- Build confidence

**Week 3:**
- Implement Stage 3 (Docker builds)
- Wait through first long build
- Enjoy fast subsequent builds

**Week 4:**
- Add Stage 4 polish
- Fine-tune as needed
- Focus on app development!

### Resources

**Documentation:**
- Conventional Commits: https://www.conventionalcommits.org/
- Semantic Versioning: https://semver.org/
- GitHub Actions: https://docs.github.com/en/actions
- Buildozer: https://buildozer.readthedocs.io/

**Tools:**
- Changelog Generator: https://github.com/mikepenz/release-changelog-builder-action
- Commit Linter: https://commitlint.js.org/
- GitHub CLI: https://cli.github.com/

**Community:**
- GitHub Actions Community: https://github.community/
- Kivy Discord: https://chat.kivy.org/

---

**Good luck with your CI/CD setup!** 🚀

Remember: Start simple (Stage 1), get comfortable, then add complexity gradually. You'll be deploying like a pro in no time!
