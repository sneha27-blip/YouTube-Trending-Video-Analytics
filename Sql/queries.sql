-- ====================================================================
-- YouTube Trending Video Analytics - Analytical SQL Queries
-- Database: Sql/youtube_trending.db
-- Table: trending_videos
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: Total Videos and Records by Country
-- Purpose: Quantifies data volume and distinguishes total trending 
-- appearances (records) from unique individual videos per country.
-- --------------------------------------------------------------------
SELECT 
    country,
    COUNT(*) AS total_trending_records,
    COUNT(DISTINCT video_id) AS unique_videos,
    ROUND(CAST(COUNT(*) AS REAL) / COUNT(DISTINCT video_id), 2) AS avg_days_per_video
FROM trending_videos
GROUP BY country
ORDER BY total_trending_records DESC;


-- --------------------------------------------------------------------
-- QUERY 2: Average and Maximum Views by Country
-- Purpose: Evaluates viewership scale and virality potential across 
-- Canada, Great Britain, India, and the United States.
-- --------------------------------------------------------------------
SELECT 
    country,
    COUNT(*) AS total_records,
    ROUND(AVG(views), 0) AS avg_views,
    MAX(views) AS max_views,
    ROUND(AVG(likes), 0) AS avg_likes,
    ROUND(AVG(comment_count), 0) AS avg_comments
FROM trending_videos
GROUP BY country
ORDER BY avg_views DESC;


-- --------------------------------------------------------------------
-- QUERY 3: Most Popular Categories in Each Country (Top 3 per Country)
-- Purpose: Identifies the dominant content categories within each 
-- geographic market using SQLite window functions.
-- --------------------------------------------------------------------
WITH CategoryRankings AS (
    SELECT 
        country,
        category_title,
        COUNT(*) AS total_records,
        ROUND(AVG(views), 0) AS avg_views,
        ROUND(AVG(engagement_rate), 2) AS avg_engagement_rate,
        ROW_NUMBER() OVER (
            PARTITION BY country 
            ORDER BY COUNT(*) DESC
        ) AS rank_in_country
    FROM trending_videos
    GROUP BY country, category_title
)
SELECT 
    country,
    rank_in_country,
    category_title,
    total_records,
    avg_views,
    avg_engagement_rate
FROM CategoryRankings
WHERE rank_in_country <= 3
ORDER BY country, rank_in_country;


-- --------------------------------------------------------------------
-- QUERY 4: Top 10 Channels by Trending Appearances
-- Purpose: Identifies which creator and media channels generate the 
-- highest volume of trending content across the entire dataset.
-- --------------------------------------------------------------------
SELECT 
    channel_title,
    GROUP_CONCAT(DISTINCT country) AS countries_active,
    COUNT(*) AS total_trending_appearances,
    COUNT(DISTINCT video_id) AS distinct_videos,
    MAX(views) AS peak_views,
    ROUND(AVG(views), 0) AS avg_views
FROM trending_videos
GROUP BY channel_title
ORDER BY total_trending_appearances DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- QUERY 5: Top 10 Videos by Total Peak Views
-- Purpose: Spotlights the most viral individual videos in the dataset 
-- based on their maximum recorded view counts.
-- --------------------------------------------------------------------
SELECT 
    video_id,
    title,
    channel_title,
    country,
    category_title,
    MAX(views) AS peak_views,
    MAX(likes) AS peak_likes,
    MAX(comment_count) AS peak_comments,
    MAX(trending_date) AS peak_trending_date
FROM trending_videos
GROUP BY video_id, country
ORDER BY peak_views DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- QUERY 6: Highest Engagement Categories
-- Purpose: Measures audience participation (likes + comments per view)
-- to reveal which genres foster the most engaged fanbases.
-- --------------------------------------------------------------------
SELECT 
    category_title,
    COUNT(*) AS total_records,
    ROUND(AVG(engagement_rate), 2) AS avg_engagement_rate,
    ROUND(AVG(like_to_view_ratio), 2) AS avg_like_to_view_ratio,
    ROUND(AVG(views), 0) AS avg_views,
    ROUND(AVG(likes), 0) AS avg_likes
FROM trending_videos
GROUP BY category_title
HAVING COUNT(*) >= 100
ORDER BY avg_engagement_rate DESC;


-- --------------------------------------------------------------------
-- QUERY 7: Average Likes, Dislikes, and Comments by Country
-- Purpose: Compares regional sentiment and interaction ratios, including 
-- the ratio of positive likes to negative dislikes.
-- --------------------------------------------------------------------
SELECT 
    country,
    ROUND(AVG(likes), 0) AS avg_likes,
    ROUND(AVG(dislikes), 0) AS avg_dislikes,
    ROUND(AVG(comment_count), 0) AS avg_comments,
    ROUND(CAST(SUM(likes) AS REAL) / NULLIF(SUM(dislikes), 0), 2) AS like_to_dislike_ratio,
    ROUND(AVG(like_to_view_ratio), 2) AS avg_like_percentage
FROM trending_videos
GROUP BY country
ORDER BY avg_likes DESC;


-- --------------------------------------------------------------------
-- QUERY 8: Publishing-Hour Analysis
-- Purpose: Determines optimal video release hours (0–23 UTC) based on 
-- trending frequency and average viewership.
-- --------------------------------------------------------------------
SELECT 
    publish_hour,
    COUNT(*) AS video_records,
    ROUND(AVG(views), 0) AS avg_views,
    ROUND(AVG(engagement_rate), 2) AS avg_engagement_rate
FROM trending_videos
GROUP BY publish_hour
ORDER BY publish_hour ASC;


-- --------------------------------------------------------------------
-- QUERY 9: Day-of-Week Publishing Analysis
-- Purpose: Evaluates video performance based on the day of the week 
-- on which the video was published.
-- --------------------------------------------------------------------
SELECT 
    publish_day_of_week,
    COUNT(*) AS video_records,
    ROUND(AVG(views), 0) AS avg_views,
    ROUND(AVG(likes), 0) AS avg_likes,
    ROUND(AVG(engagement_rate), 2) AS avg_engagement_rate
FROM trending_videos
GROUP BY publish_day_of_week
ORDER BY 
    CASE publish_day_of_week
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
        ELSE 8
    END;


-- --------------------------------------------------------------------
-- QUERY 10: Videos with the Longest Trending Duration
-- Purpose: Identifies evergreen viral videos that sustained their 
-- presence on the trending charts for the highest number of unique days.
-- --------------------------------------------------------------------
SELECT 
    video_id,
    title,
    channel_title,
    country,
    category_title,
    COUNT(DISTINCT trending_date) AS days_on_trending,
    MIN(trending_date) AS first_trending_date,
    MAX(trending_date) AS last_trending_date,
    MAX(views) AS peak_views
FROM trending_videos
GROUP BY video_id, country
ORDER BY days_on_trending DESC
LIMIT 10;
