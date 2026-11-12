-- Purpose: category-level analysis from the validated staging dataset.
-- The reference table repeats category IDs across regional files, so deduplicate it first.
-- Exact duplicate source rows are removed. Keys with conflicting row versions are excluded
-- until a business rule is approved. Literal '#NAME?' video IDs are also excluded.
WITH category_lookup AS (
    SELECT id, MAX(snippet_title) AS category_name
    FROM db_youtube_cleaned.statistics_reference_data
    GROUP BY id
),
distinct_rows AS (
    SELECT DISTINCT
        region, video_id, trending_date, title, channel_title, category_id,
        publish_time, tags, views, likes, dislikes, comment_count,
        thumbnail_link, comments_disabled, ratings_disabled,
        video_error_or_removed, description
    FROM db_youtube_cleaned.tutorial_staging_youtube
    WHERE video_id IS NOT NULL
      AND TRIM(video_id) <> ''
      AND video_id <> '#NAME?'
),
conflicting_keys AS (
    SELECT region, video_id, trending_date
    FROM distinct_rows
    GROUP BY region, video_id, trending_date
    HAVING COUNT(*) > 1
),
deduplicated AS (
    SELECT d.*
    FROM distinct_rows d
    LEFT JOIN conflicting_keys c
      ON d.region = c.region
     AND d.video_id = c.video_id
     AND d.trending_date = c.trending_date
    WHERE c.video_id IS NULL
)
SELECT
    d.region,
    c.category_name,
    COUNT(*) AS trending_observations,
    COUNT(DISTINCT d.video_id) AS distinct_videos,
    SUM(d.views) AS total_recorded_views,
    AVG(d.views) AS average_views_per_observation
FROM deduplicated d
LEFT JOIN category_lookup c
  ON d.category_id = c.id
GROUP BY d.region, c.category_name
ORDER BY d.region, total_recorded_views DESC;
