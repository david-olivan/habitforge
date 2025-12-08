# CI/CD Quick Start Guide

**Goal:** Get changelog automation working in 15 minutes

---

## Step 1: Copy Files to Your Project (5 minutes)

```bash
cd habit_tracker

# Create GitHub Actions directory
mkdir -p .github/workflows

# Copy configuration files
cp /path/to/outputs/changelog-config.json .github/
cp /path/to/outputs/release-stage1.yml .github/workflows/release.yml

# Copy commit guidelines (optional but recommended)
mkdir -p .claude/prompts
cp /path/to/outputs/claude-commit-guidelines.md .claude/prompts/commit.md

# Copy git message template (optional)
cp /path/to/outputs/gitmessage.txt .gitmessage

# Configure git to use template
git config commit.template .gitmessage
```

**What you just did:**
- Set up changelog generation workflow
- Added commit message guidelines for Claude Code
- Configured git commit template for manual commits

---

## Step 2: Commit and Push (2 minutes)

```bash
# Add new files
git add .github/ .claude/ .gitmessage

# Commit using conventional format
git commit -m "ci(release): add automated changelog generation

Set up GitHub Actions workflow to auto-generate changelogs
from conventional commits when tags are pushed."

# Push to GitHub
git push origin main
```

**What happens:**
- Nothing yet! Workflow only runs on tags, not commits.

---

## Step 3: Make Some Test Commits (3 minutes)

```bash
# Make a few commits with conventional format
git commit -m "feat(database): add habits table schema" --allow-empty
git commit -m "feat(ui): create main screen layout" --allow-empty  
git commit -m "fix(database): handle null values" --allow-empty
git commit -m "docs(readme): add installation guide" --allow-empty
git commit -m "wip: testing colors" --allow-empty

# Push commits
git push origin main
```

**Expected result:** Still nothing - waiting for a tag.

---

## Step 4: Create and Push Test Tag (2 minutes)

```bash
# Create annotated tag
git tag -a v0.0.1-test -m "Test changelog generation"

# Push the tag (THIS triggers the workflow)
git push origin v0.0.1-test
```

**What happens now:**
1. GitHub detects tag push
2. Workflow starts automatically
3. Changelog generated from commits
4. Draft release created

---

## Step 5: Check Results (3 minutes)

### Watch the Workflow Run

1. Go to GitHub repository
2. Click "Actions" tab
3. See "Release Build" workflow running
4. Click on it to watch progress
5. Should complete in ~30 seconds

### Check the Release

1. Go to "Releases" tab
2. See draft release "v0.0.1-test"
3. Click to view release notes
4. See generated changelog:

```markdown
## 🚀 Features
- feat(database): add habits table schema
- feat(ui): create main screen layout

## 🐛 Bug Fixes
- fix(database): handle null values

## 📚 Documentation
- docs(readme): add installation guide
```

Notice: The "wip" commit is NOT in changelog (ignored as configured).

---

## Step 6: Clean Up Test (1 minute)

```bash
# Delete local tag
git tag -d v0.0.1-test

# Delete remote tag
git push origin :refs/tags/v0.0.1-test

# Delete release on GitHub
# Go to Releases → click v0.0.1-test → Delete
```

---

## Step 7: Real First Release (when ready)

When you finish MVP (Stage 1 of development):

```bash
# Make sure all changes are committed
git status

# Create real version tag
git tag -a v0.1.0 -m "MVP Release - Basic habit tracking"

# Push it
git push origin v0.1.0

# Wait 30 seconds
# Go to Releases → Edit draft → Publish
```

**You now have:**
- Automated changelog generation
- Professional release notes
- Version tracking via tags

---

## Using with Claude Code

When working with Claude Code, reference the commit guidelines:

```
You: "Please read .claude/prompts/commit.md and follow those 
     guidelines for all commits."

Claude Code: "I'll follow the conventional commit format. 
             Let me review the changes..."
```

Or more simply:

```
You: "Commit these changes using conventional commit format"

Claude Code: [analyzes changes]
"I suggest: feat(ui): add color picker component

Does this look good?"
```

---

## Daily Workflow

### During Development (No Tags)

```bash
# Work on features
git commit -m "feat(habits): add streak calculation"
git commit -m "feat(ui): implement heatmap visualization"
git commit -m "fix(ui): correct button alignment"
git push origin main

# Repeat... no releases created yet
```

### When Ready to Release

```bash
# All features done, everything committed
git status  # Should be clean

# Create version tag
git tag -a v0.2.0 -m "Phase 2: Enhanced features"
git push origin v0.2.0

# 30 seconds later: changelog ready!
# Review draft release, then publish
```

### Version Numbering

- **v0.1.0** - MVP (first working version)
- **v0.2.0** - Add new features (Phase 2)
- **v0.3.0** - More features (Phase 3)
- **v0.3.1** - Bug fix
- **v1.0.0** - Stable release (when you use it daily)

---

## Troubleshooting

### Workflow Didn't Run

**Check:**
1. Tag matches pattern `v*.*.*` (e.g., v0.1.0, not 0.1.0)
2. File is in `.github/workflows/release.yml`
3. GitHub Actions is enabled (Settings → Actions)

**Verify:**
```bash
git tag  # Should show: v0.0.1-test
ls .github/workflows/  # Should show: release.yml
```

### Changelog is Empty

**Cause:** No conventional commits since last tag (or no last tag)

**Fix:** Make sure commits follow format:
```bash
git log --oneline  # Check commit messages
# Should see: "feat(scope): message" format
```

### Release Not Created

**Check Actions logs:**
1. Go to Actions tab
2. Click on failed workflow
3. Expand steps to see error
4. Common issue: `GITHUB_TOKEN` permissions

**Fix:** Settings → Actions → Workflow permissions → Read and write

---

## Next Steps

Once this works:

### Week 2: Add Version Bumping
- Copy `release-stage3.yml` over `release.yml`
- Remove Docker build steps (not ready yet)
- Test version updates in buildozer.spec

### Week 3: Add Docker Builds
- Use full `release-stage3.yml`
- First build takes 30-45 minutes
- Subsequent builds: 5-10 minutes

### Week 4: Polish
- Add status badges
- Configure notifications
- Optimize caching

---

## Quick Commands Reference

```bash
# Create and push tag (triggers release)
git tag -a v0.1.0 -m "Release message"
git push origin v0.1.0

# Delete tag (if mistake)
git tag -d v0.1.0
git push origin :refs/tags/v0.1.0

# View tags
git tag -l

# View commits since last tag
git log v0.1.0..HEAD --oneline

# Commit with conventional format
git commit -m "feat(scope): message"
git commit -m "fix(scope): message"
git commit -m "docs(scope): message"
```

---

## Success Checklist

After setup, you should have:

- [x] `.github/workflows/release.yml` file
- [x] `.github/changelog-config.json` file
- [x] Files committed and pushed
- [x] Test tag created and pushed
- [x] Workflow ran successfully
- [x] Draft release with changelog created
- [x] Test tag and release deleted
- [x] Understanding of workflow

**If all checked: You're ready to use CI/CD! 🎉**

---

## Getting Help

**Check logs:**
```bash
# View workflow runs
gh run list --workflow=release.yml

# View specific run logs
gh run view <run-id> --log
```

**Common issues:**
1. Tag format wrong → Use `v0.1.0` not `0.1.0`
2. No commits → Make at least one commit before tagging
3. Permissions → Check Actions workflow permissions
4. File location → Must be in `.github/workflows/`

**Still stuck?**
- Check Actions tab for error details
- Review CICD_SETUP_MANUAL.md troubleshooting section
- Verify files match templates exactly

---

**Time to first working release: 15 minutes**  
**Time saved per release: 30 minutes**  
**ROI: After 1st release!** 🚀
