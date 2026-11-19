-- ====================================================================
-- YouTube Trending Video Analytics - Database Schema
-- Database: Sql/youtube_trending.db
-- Table: trending_videos
-- ====================================================================

-- Drop table if it already exists to allow clean re-runs
DROP TABLE IF EXISTS trending_videos;

-- Main trending videos table
CREATE TABLE trending_videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT NOT NULL,
    trending_date TEXT NOT NULL,
    title TEXT,
    channel_title TEXT,
    category_id INTEGER,
    category_title TEXT,
    publish_time TEXT,
    publish_date TEXT,
    publish_hour INTEGER,
    publish_day_of_week TEXT,
    tags TEXT,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    dislikes INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    thumbnail_link TEXT,
    comments_disabled INTEGER DEFAULT 0,
    ratings_disabled INTEGER DEFAULT 0,
    video_error_or_removed INTEGER DEFAULT 0,
    description TEXT,
    country TEXT NOT NULL,
    engagement_rate REAL DEFAULT 0.0,
    like_to_view_ratio REAL DEFAULT 0.0,
    days_to_trend INTEGER DEFAULT 0
);

-- ====================================================================
-- Indexes for High-Performance Analytical Queries
-- ====================================================================

CREATE INDEX IF NOT EXISTS idx_country ON trending_videos(country);
CREATE INDEX IF NOT EXISTS idx_video_id ON trending_videos(video_id);
CREATE INDEX IF NOT EXISTS idx_category_title ON trending_videos(category_title);
CREATE INDEX IF NOT EXISTS idx_trending_date ON trending_videos(trending_date);
CREATE INDEX IF NOT EXISTS idx_channel_title ON trending_videos(channel_title);
CREATE INDEX IF NOT EXISTS idx_country_category ON trending_videos(country, category_title);
CREATE INDEX IF NOT EXISTS idx_video_country ON trending_videos(video_id, country);
