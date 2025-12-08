-- HabitForge Database Schema
-- SQLite3 Database Schema for Habit Tracking Application
-- Version: 1.0
-- Last Updated: December 8, 2024

-- ============================================
-- HABITS TABLE
-- ============================================
-- Stores habit definitions and configurations
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    color TEXT NOT NULL,
    goal_type TEXT NOT NULL CHECK(goal_type IN ('daily', 'weekly', 'monthly')),
    goal_count INTEGER NOT NULL CHECK(goal_count > 0 AND goal_count <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived INTEGER DEFAULT 0,
    UNIQUE(name COLLATE NOCASE)  -- Case-insensitive unique constraint for habit names
);

-- ============================================
-- COMPLETIONS TABLE
-- ============================================
-- Stores individual habit completion records
-- Each row represents one or more completions on a specific date
-- IMPLEMENTED in Phase 2 (Section 2.1.2)
CREATE TABLE IF NOT EXISTS completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date DATE NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    UNIQUE(habit_id, date)  -- One record per habit per date
);

-- ============================================
-- SETTINGS TABLE (Future - Phase 3)
-- ============================================
-- Stores app-wide configuration and user preferences
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
-- Composite index on (habit_id, date) for faster habit-specific date queries
CREATE INDEX IF NOT EXISTS idx_completions_habit_date
ON completions(habit_id, date);

-- Index on habits.archived for faster filtering of active habits
CREATE INDEX IF NOT EXISTS idx_habits_archived
ON habits(archived);

-- ============================================
-- NOTES
-- ============================================
-- 1. COLLATE NOCASE ensures habit names are unique regardless of case
-- 2. CASCADE delete ensures completions are removed when habit is deleted
-- 3. goal_type CHECK constraint enforces valid values at database level
-- 4. goal_count CHECK constraint enforces valid range (1-100)
-- 5. Indexes improve query performance for common operations