-- Purpose: quantify duplicate business keys, separating exact and conflicting rows.
-- Business key: region + video_id + trending_date. Invalid '#NAME?' IDs are excluded.
WITH grouped AS (
    SELECT
        region,
        video_id,
        trending_date,
        COUNT(*) AS copies,
        COUNT(DISTINCT CONCAT_WS('|',
            COALESCE(title, ''),
            COALESCE(channel_title, ''),
            COALESCE(CAST(category_id AS VARCHAR), ''),
            COALESCE(publish_time, ''),
            COALESCE(tags, ''),
            COALESCE(CAST(views AS VARCHAR), ''),
            COALESCE(CAST(likes AS VARCHAR), ''),
            COALESCE(CAST(dislikes AS VARCHAR), ''),
            COALESCE(CAST(comment_count AS VARCHAR), ''),
            COALESCE(thumbnail_link, ''),
            COALESCE(CAST(comments_disabled AS VARCHAR), ''),
            COALESCE(CAST(ratings_disabled AS VARCHAR), ''),
            COALESCE(CAST(video_error_or_removed AS VARCHAR), ''),
            COALESCE(description, '')
        )) AS distinct_row_variants
    FROM db_youtube_cleaned.tutorial_staging_youtube
    WHERE video_id IS NOT NULL
      AND TRIM(video_id) <> ''
      AND video_id <> '#NAME?'
    GROUP BY region, video_id, trending_date
    HAVING COUNT(*) > 1
)
SELECT
    COUNT(*) AS duplicate_key_groups,
    SUM(copies - 1) AS duplicate_extra_rows,
    SUM(CASE WHEN distinct_row_variants = 1 THEN copies - 1 ELSE 0 END)
        AS exact_duplicate_extra_rows,
    SUM(CASE WHEN distinct_row_variants > 1 THEN copies - 1 ELSE 0 END)
        AS conflicting_duplicate_extra_rows,
    SUM(CASE WHEN distinct_row_variants > 1 THEN 1 ELSE 0 END)
        AS conflicting_key_groups
FROM grouped;
