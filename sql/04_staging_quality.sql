-- Purpose: profile core quality checks on the staging table.
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT region) AS regions,
    SUM(CASE WHEN video_id IS NULL OR TRIM(video_id) = '' THEN 1 ELSE 0 END)
        AS blank_video_ids,
    SUM(CASE WHEN video_id = '#NAME?' THEN 1 ELSE 0 END)
        AS formula_error_video_ids,
    SUM(CASE WHEN region IS NULL OR TRIM(region) = '' THEN 1 ELSE 0 END)
        AS blank_regions,
    SUM(CASE WHEN views < 0 OR likes < 0 OR dislikes < 0 OR comment_count < 0 THEN 1 ELSE 0 END)
        AS negative_metric_rows
FROM db_youtube_cleaned.tutorial_staging_youtube;

SELECT region, COUNT(*) AS row_count
FROM db_youtube_cleaned.tutorial_staging_youtube
GROUP BY region
ORDER BY region;
