# Commit Message Guidelines for Claude Code

## MANDATORY: Use Conventional Commits Format

Every commit message MUST follow this structure:

```
<type>(<scope>): <subject>

<optional body>

<optional footer>
```

## Commit Types

Use these types (and ONLY these types):

- **feat**: New feature visible to users
  - Example: `feat(habits): add streak calculation with flame icon`
  
- **fix**: Bug fix that resolves an issue
  - Example: `fix(database): prevent duplicate habit names`
  
- **docs**: Documentation changes only (no code changes)
  - Example: `docs(readme): add build instructions for Android`
  
- **style**: Code formatting, whitespace, missing semicolons (no logic change)
  - Example: `style(ui): fix indentation in habit card component`
  
- **refactor**: Code restructuring without changing behavior
  - Example: `refactor(habits): extract validation logic to separate function`
  
- **perf**: Performance improvement
  - Example: `perf(database): add index on habit_id for faster queries`
  
- **test**: Adding or updating tests
  - Example: `test(habits): add unit tests for streak calculation`
  
- **chore**: Maintenance tasks, dependencies, build config
  - Example: `chore(deps): upgrade kivy to version 2.2.1`
  
- **ci**: CI/CD pipeline changes
  - Example: `ci(release): add Docker caching for faster builds`

## Scopes

Use these scopes based on what area of code is affected:

- **habits**: Habit management logic (CRUD, calculations, validation)
- **ui**: User interface components and screens
- **database**: Database operations, schema, queries
- **analytics**: Statistics, visualizations, reports
- **build**: Build system, buildozer configuration
- **ci**: GitHub Actions, CI/CD workflows

## Subject Line Rules

1. **Use imperative mood**: "add" not "added" or "adds"
   - Good: `feat(ui): add color picker component`
   - Bad: `feat(ui): added color picker component`

2. **Keep it short**: Maximum 50 characters
   - If longer, move details to body

3. **Start with lowercase**: After the colon
   - Good: `feat(habits): add streak tracking`
   - Bad: `feat(habits): Add Streak Tracking`

4. **No period at the end**
   - Good: `fix(ui): correct button alignment`
   - Bad: `fix(ui): correct button alignment.`

5. **Be specific but concise**
   - Good: `feat(habits): implement weekly goal tracking`
   - Bad: `feat(habits): add stuff`

## Body Guidelines (Optional)

Use the body to explain:
- **WHAT** changed (if not obvious from subject)
- **WHY** you made the change
- **HOW** it works (if complex)

Format:
- Wrap at 72 characters
- Leave blank line between subject and body
- Use bullet points for multiple items

Example:
```
feat(habits): add streak calculation logic

Implemented algorithm to track consecutive goal completions:
- Daily habits: count consecutive days
- Weekly habits: count consecutive weeks
- Monthly habits: count consecutive months

Streak resets to 0 when user misses a goal period.
Closes #15
```

## Footer Guidelines (Optional)

Use footer for:
- **Breaking changes**: `BREAKING CHANGE: description`
- **Issue references**: `Closes #123` or `Fixes #456`
- **Deprecation notices**: `DEPRECATED: old method no longer supported`

## Examples

### Feature Addition
```
feat(ui): implement color picker for habit creation

Added color picker component with 8 preset colors.
Users can now customize habit colors when creating new habits.
Component is reusable across different forms.
```

### Bug Fix
```
fix(database): handle null values in habit name field

Previously, app crashed when habit name was null.
Now validates input and shows error message to user.

Fixes #42
```

### Documentation
```
docs(readme): add installation instructions for Linux

Added step-by-step guide for setting up development environment
on Ubuntu 20.04 and 22.04.
```

### Refactoring
```
refactor(habits): extract validation logic to separate module

Moved validation functions from habit_manager.py to new
validators.py module for better code organization and reusability.
```

### Breaking Change
```
feat(database): change habit table schema structure

BREAKING CHANGE: Habit table now uses goal_type enum instead of
separate boolean fields. Existing databases must be migrated.

Migration script: scripts/migrate_v0_to_v1.py
```

## Process When Committing

1. **Review changes first**
   ```bash
   git status
   git diff
   ```

2. **Stage files**
   ```bash
   git add <files>
   ```

3. **Analyze the changes:**
   - What area does this affect? (determines scope)
   - Is this a feature, fix, or maintenance? (determines type)
   - What's the one-sentence summary? (becomes subject)

4. **Write commit message:**
   ```bash
   git commit -m "type(scope): subject
   
   Optional body explaining more details.
   
   Optional footer with references."
   ```

5. **Verify format:**
   - Type is one of the allowed types
   - Scope matches project areas
   - Subject is imperative, lowercase, under 50 chars
   - Body wraps at 72 chars if present

## Bad Examples (Do NOT do this)

❌ `git commit -m "fixed stuff"`
- No type, no scope, vague subject

❌ `git commit -m "feat: Added new feature"`
- Not imperative mood ("Added" → "add")

❌ `git commit -m "update code"`
- No type, no scope, too vague

❌ `git commit -m "feat(ui): Add color picker, fix button bug, update docs"`
- Multiple unrelated changes in one commit

❌ `git commit -m "WIP"`
- No meaningful description

## Good Examples

✅ `feat(habits): add streak calculation logic`
✅ `fix(database): prevent duplicate habit names`
✅ `docs(readme): add build instructions`
✅ `refactor(ui): extract color picker to component`
✅ `perf(database): add index on habit_id`
✅ `test(analytics): add streak calculation tests`
✅ `chore(deps): upgrade kivymd to 1.1.1`
✅ `ci(release): add Docker build caching`

## Integration with CI/CD

Your commit messages directly affect:

1. **Changelog generation**: 
   - `feat` commits → "Features" section
   - `fix` commits → "Bug Fixes" section
   - `docs` commits → "Documentation" section

2. **Version bumping** (future):
   - `feat` → bump MINOR version (0.1.0 → 0.2.0)
   - `fix` → bump PATCH version (0.1.0 → 0.1.1)
   - `BREAKING CHANGE` → bump MAJOR version (0.1.0 → 1.0.0)

3. **Release notes**:
   - Good commits = clear, professional release notes
   - Bad commits = messy, unclear release notes

## When Working with Claude Code

When I (Claude Code) suggest commits, I will:

1. Analyze the changes made
2. Determine appropriate type and scope
3. Write a clear, imperative subject
4. Add body if changes are complex
5. Reference issues if applicable
6. Ask for your approval before committing

You can say:
- "Commit these changes" → I'll analyze and suggest format
- "Use conventional commits" → I'll follow these guidelines
- "Review my changes and commit" → I'll examine diff first

## Validation

Before every commit, verify:
- [ ] Type is valid (feat, fix, docs, etc.)
- [ ] Scope matches project areas
- [ ] Subject is imperative mood
- [ ] Subject is under 50 characters
- [ ] Subject has no period at end
- [ ] Body wraps at 72 characters (if present)
- [ ] Footer references issues (if applicable)

## Quick Reference

**Template:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Common patterns:**
- New UI component: `feat(ui): add <component> component`
- Bug fix: `fix(<area>): resolve <issue>`
- Database change: `feat(database): add <table/field>`
- Documentation: `docs(<file>): add/update <content>`
- Refactor: `refactor(<area>): <what changed>`
- Build config: `chore(build): <what changed>`
- CI/CD: `ci(<workflow>): <what changed>`

---

**Remember: Consistent, clear commit messages make the entire project more maintainable and professional. Follow these guidelines strictly.**
